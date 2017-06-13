from CouchInterface import CouchInterface

couch_handle = CouchInterface()

# couch_handle.set_assigned(['5377-13319239','5377-13364921','sdfgdsfg'],'triager_tickets')
couch_handle.reset_assigned('triager_tickets')