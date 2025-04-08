from ldap3 import Server, Connection, MOCK_SYNC, ALL

from backend.type import LoginData

class	LDAP:
	def	__init__(self):
		self.server = Server("my_fake_server", get_info=ALL)
		self.connection = Connection(self.server, client_strategy=MOCK_SYNC)
		self.connection.bind()
		self.BASE_DN = "ou=users,dc=example,dc=com"
		self.init_fake_ldap()

	def init_fake_ldap(self):
		# Crée l"unité organisationnelle
		self.entry_add(self.BASE_DN, {"objectClass": ["organizationalUnit"]})
		# Crée un utilisateur de test - Admin
		self.entry_add(f"cn=admin,{self.BASE_DN}", {
			"objectClass"	: ["inetOrgPerson"],
			"cn"			: "admin",
			"sn"			: "admin",
			"givenName"		: "admin",
			"mail"			: "admin",
			"userPassword"	: "admin"
		})
		# Crée un utilisateur de test - Test
		self.entry_add(f"cn=test,{self.BASE_DN}", {
			"objectClass"	: ["inetOrgPerson"],
			"cn"			: "test",
			"sn"			: "test",
			"givenName"		: "test",
			"mail"			: "test",
			"userPassword"	: "test"
		})

	def	get_access(self, data: LoginData):
		if not self.connection:
			return None
		self.search(self.BASE_DN, f"(cn={data.username})", attributes=["cn", "sn", "givenName", "mail", "userPassword"])
		return self.connection.entries

	def	search(self, search_base, search_filter, attributes=None):
		if not self.connection:
			return None
		return self.connection.search(search_base, search_filter, attributes=attributes)

	def	entry_add(self, dn, attributes):
		if not self.connection:
			return None
		return self.connection.strategy.add_entry(dn, attributes)

	def	entry_update(self, dn, attributes):
		if not self.connection:
			return None
		return self.connection.modify(dn, attributes)

	def	entry_delete(self, dn):
		if not self.connection:
			return None
		return self.connection.delete(dn)
	
	def	disconnect(self):
		if self.connection:
			self.connection.unbind()
