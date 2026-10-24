import csv
import io
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash
from app import create_app
from app.db import get_db
from app.services import now_local

class SystemTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.app=create_app({'TESTING':True,'DATABASE':str(Path(self.tmp.name)/'test.db'),'SECRET_KEY':'test'})
        self.client=self.app.test_client()
        with self.app.app_context():
            db=get_db()
            for i, role in [(1,'admin'),(2,'student'),(3,'student')]:
                db.execute('INSERT INTO users(id,name,email,password_hash,role) VALUES(?,?,?,?,?)',(i,'User '+str(i),f'u{i}@test.az',generate_password_hash('Password123'),role))
            db.commit()
        self.login(1)
        self.data=dict(title='Python seminarı',description='Praktiki seminar',category_id=1,starts_at=(now_local()+timedelta(days=10)).isoformat(timespec='minutes'),location='Bakı',capacity=2)
        self.event=self.send('/events',data=self.data).json['id']
    def tearDown(self): self.tmp.cleanup()
    def send(self,path,method='POST',data=None,client=None):
        c=client or self.client
        token=c.get('/api/session').json['csrf']
        return c.open('/api'+path,method=method,json={} if data is None else data,headers={'X-CSRF-Token':token})
    def login(self,i,client=None): return self.send('/login',data={'email':f'u{i}@test.az','password':'Password123'},client=client)
    def reg(self): return f'/events/{self.event}/registration'
    def test_crud(self):
        self.assertEqual(self.send(f'/events/{self.event}','PUT',dict(self.data,title='Yeni ad')).status_code,200)
        self.assertEqual(self.client.get('/api/events').json[0]['title'],'Yeni ad')
        self.assertEqual(self.send(f'/events/{self.event}','DELETE').status_code,200)
        self.assertEqual(self.client.get('/api/events').json,[])
    def test_filters(self):
        for q in ['q=Python','category=1&location=Bakı','from=2000-01-01&to=2999-12-31']:
            self.assertEqual(len(self.client.get('/api/events?'+q).json),1)
        self.assertEqual(self.client.get('/api/events?q=missing').json,[])
        self.assertEqual(self.client.get('/api/events?q=%27%20OR%201=1--').json,[])
    def test_invalid_fields(self):
        for change in [dict(title=' '),dict(title=None),dict(capacity=0),dict(capacity='1.5'),dict(starts_at='2020-01-01T10:00'),dict(starts_at='bad'),dict(category_id=999)]:
            self.assertEqual(self.send('/events',data=dict(self.data,**change)).status_code,400)
    def test_auth_csrf(self):
        self.assertEqual(self.send('/login',data={'email':'u1@test.az','password':'bad'}).status_code,401)
        self.login(2)
        self.assertEqual(self.send('/events',data=self.data).status_code,403)
        self.assertEqual(self.client.get('/api/stats').status_code,403)
        self.assertEqual(self.client.post('/api/events',json=self.data).status_code,403)
        self.send('/logout')
        self.assertEqual(self.send(self.reg()).status_code,401)
    def test_registration_duplicate_cancel(self):
        self.login(2)
        self.assertEqual(self.send(self.reg()).status_code,201)
        self.assertEqual(self.send(self.reg()).status_code,409)
        self.assertEqual(len(self.client.get('/api/events?mine=1').json),1)
        self.assertEqual(self.send(self.reg(),'DELETE').status_code,200)
        self.assertEqual(self.client.get('/api/events?mine=1').json,[])
    def test_capacity_and_update(self):
        self.send(f'/events/{self.event}','PUT',dict(self.data,capacity=1))
        self.login(2);self.send(self.reg());self.login(3)
        self.assertEqual(self.send(self.reg()).status_code,409)
        self.login(1);self.send(f'/events/{self.event}','PUT',dict(self.data,capacity=2))
        self.login(3);self.send(self.reg());self.login(1)
        self.assertEqual(self.send(f'/events/{self.event}','PUT',dict(self.data,capacity=1)).status_code,409)
    def test_concurrent_last_place(self):
        self.send(f'/events/{self.event}','PUT',dict(self.data,capacity=1))
        clients=[self.app.test_client(),self.app.test_client()]
        self.login(2,clients[0]);self.login(3,clients[1])
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda c:self.send(self.reg(),client=c).status_code,clients))
        self.assertEqual(sorted(results),[201,409])
        self.assertEqual(self.client.get('/api/events').json[0]['registered'],1)
    def test_past_event(self):
        with self.app.app_context():
            db=get_db();db.execute('UPDATE events SET starts_at=? WHERE id=?',('2020-01-01T10:00',self.event));db.commit()
        self.login(2)
        self.assertTrue(self.client.get('/api/events').json[0]['past'])
        self.assertEqual(self.send(self.reg()).status_code,409)
    def test_stats_export_cascade(self):
        self.login(2);self.send(self.reg())
        self.assertEqual(self.client.get(f'/api/events/{self.event}/participants.csv').status_code,403)
        self.login(1);stats=self.client.get('/api/stats').json
        self.assertEqual((stats['events'],stats['registrations']),(1,1))
        self.assertEqual(stats['popular'][0]['count'],1)
        rows=list(csv.reader(io.StringIO(self.client.get(f'/api/events/{self.event}/participants.csv').data.decode('utf-8-sig'))))
        self.assertEqual(rows[1][1],'u2@test.az')
        self.send(f'/events/{self.event}','DELETE')
        self.assertEqual(self.client.get('/api/stats').json['registrations'],0)
    def test_signup(self):
        data=dict(name='Yeni İstifadəçi',email='new@test.az',password='Password123')
        self.assertEqual(self.send('/signup',data=data).status_code,201)
        self.assertEqual(self.send('/signup',data=dict(data,email='NEW@test.az')).status_code,409)
        self.assertEqual(self.send('/signup',data=dict(data,email='bad')).status_code,400)
        with self.app.app_context():
            row=get_db().execute('SELECT password_hash,role FROM users WHERE email=?',('new@test.az',)).fetchone()
            self.assertNotEqual(row['password_hash'],'Password123');self.assertEqual(row['role'],'student')
    def test_database_constraints(self):
        with self.app.app_context():
            db=get_db();db.execute('INSERT INTO registrations(user_id,event_id) VALUES(2,?)',(self.event,));db.commit()
            with self.assertRaises(sqlite3.IntegrityError): db.execute('INSERT INTO registrations(user_id,event_id) VALUES(2,?)',(self.event,))
            db.rollback()
            with self.assertRaises(sqlite3.IntegrityError): db.execute('INSERT INTO registrations(user_id,event_id) VALUES(999,?)',(self.event,))
            db.rollback()
    def test_csv_formula_escape(self):
        with self.app.app_context():
            db=get_db();db.execute("UPDATE users SET name='=1+1' WHERE id=2");db.commit()
        self.login(2);self.send(self.reg());self.login(1)
        rows=list(csv.reader(io.StringIO(self.client.get(f'/api/events/{self.event}/participants.csv').data.decode('utf-8-sig'))))
        self.assertEqual(rows[1][0],"'=1+1")
    def test_missing_and_invalid_json(self):
        self.assertEqual(self.send('/events/999','PUT',self.data).status_code,404)
        self.assertEqual(self.send('/events/999/registration').status_code,404)
        self.assertEqual(self.send('/events/999','DELETE').status_code,404)
        self.assertEqual(self.send('/events',data=['bad']).status_code,400)
    def test_frontend_headers(self):
        response=self.client.get('/')
        self.assertEqual(response.status_code,200);self.assertIn(b'UniEvent',response.data)
        self.assertEqual(response.headers['X-Frame-Options'],'DENY')
        asset=self.client.get('/static/app.js')
        self.assertEqual(asset.status_code,200)
        asset.close()
if __name__=='__main__': unittest.main()
