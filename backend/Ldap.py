from ldap3 import Server, Connection, MOCK_SYNC, ALL

from backend.type import LoginData

class	LDAP:
	def	__init__(self):
		self._server = Server("my_fake_server", get_info=ALL)
		self._connection = Connection(self._server, client_strategy=MOCK_SYNC)
		self._connection.bind()
		self._BASE_DN = "ou=users,dc=example,dc=com"
		self._init_fake_ldap()

	def _init_fake_ldap(self):
		# Crée l"unité organisationnelle
		self.entry_add(self._BASE_DN, {"objectClass": ["organizationalUnit"]})
		# Crée un utilisateur de test - Admin
		self.entry_add(f"cn=admin,{self._BASE_DN}", {
			"objectClass"	: ["inetOrgPerson"],
			"cn"			: "admin",
			"sn"			: "admin",
			"givenName"		: "admin",
			"mail"			: "admin",
			"userPassword"	: "admin"
		})
		# Crée un utilisateur de test - Test
		self.entry_add(f"cn=test,{self._BASE_DN}", {
			"objectClass"	: ["inetOrgPerson"],
			"cn"			: "test",
			"sn"			: "test",
			"givenName"		: "test",
			"mail"			: "test",
			"userPassword"	: "test"
		})

	def	get_access(self, data: LoginData):
		if not self._connection:
			return None
		self.search(self._BASE_DN, f"(cn={data.username})", attributes=["cn", "sn", "givenName", "mail", "userPassword"])
		return self._connection.entries

	def	search(self, search_base, search_filter, attributes=None):
		if not self._connection:
			return None
		return self._connection.search(search_base, search_filter, attributes=attributes)

	def	entry_add(self, dn, attributes):
		if not self._connection:
			return None
		return self._connection.strategy.add_entry(dn, attributes)

	def	entry_update(self, dn, attributes):
		if not self._connection:
			return None
		return self._connection.modify(dn, attributes)

	def	entry_delete(self, dn):
		if not self._connection:
			return None
		return self._connection.delete(dn)
	
	def	disconnect(self):
		if self._connection:
			self._connection.unbind()
