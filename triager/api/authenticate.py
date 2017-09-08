import ldap
import traceback
import json
import os

ldap_config = {}

with open(os.path.join(os.path.dirname(__file__),'ldap.json')) as fp:
	ldap_config = json.load(fp)

# l = ldap.initialize("ldap://"+ldap_config['host'])

username = "arjun@ibm.com"
# username = "cn="+username+","+ldap_config['baseDN']
password = "root"

# try:
# 	l.protocol_version = ldap.VERSION3
# 	l.simple_bind_s(username, password)
# 	valid = True
# 	print "Connected"
# except Exception:
# 	print "Not connected"
# 	print traceback.format_exc()

try:
	l = ldap.open(ldap_config['host'])
	l.protocol_version = ldap.VERSION3

	baseDN = ldap_config['baseDN']
	searchScope = ldap.SCOPE_SUBTREE
	retrieveAttributes = ['cn', 'dn']
	searchFilter = ldap_config['usernameAttribute']+"="+username
	
	# baseDN = "ou=bluepages,dc=example,dc=com"
	# searchScope = ldap.SCOPE_SUBTREE
	# retrieveAttributes = None
	# searchFilter = "mail=arjun@ibm.com"	

	try:
		ldap_result_id = l.search(baseDN, searchScope, searchFilter, retrieveAttributes)
		result_set = []
		while True:
			result_type, result_data = l.result(ldap_result_id, 0)
			print result_data
			if result_data == []:
				break
			else:
				if result_type == ldap.RES_SEARCH_ENTRY:
					result_set.append(result_data)
		print result_set
	
	except ldap.LDAPError:
		traceback.format_exc()

except Exception:
	traceback.format_exc()