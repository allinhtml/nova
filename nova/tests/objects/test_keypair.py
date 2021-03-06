#    Copyright 2013 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime

from nova import context
from nova import db
from nova.objects import keypair
from nova.openstack.common import timeutils
from nova.tests.objects import test_objects

NOW = timeutils.utcnow().replace(microsecond=0)
fake_keypair = {
    'created_at': NOW,
    'updated_at': None,
    'deleted_at': None,
    'deleted': False,
    'id': 123,
    'name': 'foo-keypair',
    'user_id': 'fake-user',
    'fingerprint': 'fake-fingerprint',
    'public_key': 'fake\npublic\nkey',
    }


class _TestKeyPairObject(object):
    def _compare(self, obj, db_obj):
        for key in obj.fields:
            obj_val = obj[key]
            if isinstance(obj_val, datetime.datetime):
                obj_val = obj_val.replace(tzinfo=None)
            db_val = db_obj[key]
            self.assertEqual(db_val, obj_val)

    def test_get_by_name(self):
        ctxt = context.get_admin_context()
        self.mox.StubOutWithMock(db, 'key_pair_get')
        db.key_pair_get(ctxt, 'fake-user', 'foo-keypair').AndReturn(
            fake_keypair)
        self.mox.ReplayAll()
        keypair_obj = keypair.KeyPair.get_by_name(ctxt, 'fake-user',
                                                  'foo-keypair')
        self._compare(keypair_obj, fake_keypair)

    def test_create(self):
        ctxt = context.get_admin_context()
        self.mox.StubOutWithMock(db, 'key_pair_create')
        db.key_pair_create(ctxt,
                           {'name': 'foo-keypair',
                            'public_key': 'keydata'}).AndReturn(fake_keypair)
        self.mox.ReplayAll()
        keypair_obj = keypair.KeyPair()
        keypair_obj.name = 'foo-keypair'
        keypair_obj.public_key = 'keydata'
        keypair_obj.create(ctxt)
        self._compare(keypair_obj, fake_keypair)

    def test_destroy(self):
        ctxt = context.get_admin_context()
        self.mox.StubOutWithMock(db, 'key_pair_destroy')
        db.key_pair_destroy(ctxt, 'fake-user', 'foo-keypair')
        self.mox.ReplayAll()
        keypair_obj = keypair.KeyPair()
        keypair_obj.id = 123
        keypair_obj.user_id = 'fake-user'
        keypair_obj.name = 'foo-keypair'
        keypair_obj.destroy(ctxt)

    def test_destroy_by_name(self):
        ctxt = context.get_admin_context()
        self.mox.StubOutWithMock(db, 'key_pair_destroy')
        db.key_pair_destroy(ctxt, 'fake-user', 'foo-keypair')
        self.mox.ReplayAll()
        keypair.KeyPair.destroy_by_name(ctxt, 'fake-user', 'foo-keypair')

    def test_get_by_user(self):
        ctxt = context.get_admin_context()
        self.mox.StubOutWithMock(db, 'key_pair_get_all_by_user')
        self.mox.StubOutWithMock(db, 'key_pair_count_by_user')
        db.key_pair_get_all_by_user(ctxt, 'fake-user').AndReturn(
            [fake_keypair])
        db.key_pair_count_by_user(ctxt, 'fake-user').AndReturn(1)
        self.mox.ReplayAll()
        keypairs = keypair.KeyPairList.get_by_user(ctxt, 'fake-user')
        self.assertEqual(1, len(keypairs))
        self._compare(keypairs[0], fake_keypair)
        self.assertEqual(1, keypair.KeyPairList.get_count_by_user(ctxt,
                                                                  'fake-user'))


class TestMigrationObject(test_objects._LocalTest,
                          _TestKeyPairObject):
    pass


class TestRemoteMigrationObject(test_objects._RemoteTest,
                                _TestKeyPairObject):
    pass
