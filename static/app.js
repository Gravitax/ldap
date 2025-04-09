let				_TOKEN = null;

const			api_set_response = (response = null) => {
	const	api_response = document.getElementById("api_response");

	if (response != null && api_response != null) 
		api_response.innerHTML = `status: ${response.status} - ${response.message}`;
	return (response.message != "invalid token");
};

async function	login() {
	const	login = document.getElementById("login").value;
	const	password = document.getElementById("password").value;
	const	response = await fetch("/login", {
		method	: "POST",
		headers	: { "Content-Type": "application/json" },
		body	: JSON.stringify({ username: login, password: password })
	});
	const	data = await response.json();

	api_set_response(data);
	if (data.status == 200) {
		const	elt_login = document.getElementById("elt_login");
		const	elt_content = document.getElementById("elt_content");

		elt_login.classList.add("hidden");
		elt_content.classList.remove("hidden");
		_TOKEN = data.token;
	}
};

function		delog() {
	const	elt_login = document.getElementById("elt_login");
	const	elt_content = document.getElementById("elt_content");
	const	api_response = document.getElementById("api_response");
	
	_TOKEN = null;
	elt_login?.classList.remove("hidden");
	elt_content?.classList.add("hidden");
	api_response.innerHTML = "";
};

// ========== HTPASSWD

async function	htpasswd_list() {
	const	response = await fetch(`/htpasswd/list?token=${encodeURIComponent(_TOKEN)}`, {
		method	: "GET",
	});
	const	data = await response.json();
	
	setTimeout(() => {
		if (api_set_response(data) == false)
			return ;
		const	list = document.getElementById("htpasswd_list");

		list.innerHTML = "";
		data.data.forEach(user => {
			const	li = document.createElement("li");
			const	btn = document.createElement("button");
	
			li.textContent = `${user.username} - ${user.password}`;
			btn.textContent = "delete";
			btn.onclick = () => htpasswd_delete(user.username);
			li.appendChild(btn);
			list.appendChild(li);
		});
	}, 1000);
};

async function	htpasswd_add() {
	const	username = document.getElementById("htpasswd_new").value;
	const	response = await fetch("/htpasswd/add", {
		method	: "POST",
		headers	: { "Content-Type": "application/json" },
		body	: JSON.stringify({ token: _TOKEN, username })
	});
	const	data = await response.json();

	if (api_set_response(data) == false)
		return ;
	htpasswd_list();
};

async function	htpasswd_delete(username) {
	const	response = await fetch("/htpasswd/delete", {
		method	: "POST",
		headers	: { "Content-Type": "application/json" },
		body	: JSON.stringify({ token: _TOKEN, username })
	});
	const	data = await response.json();

	if (api_set_response(data) == false)
		return ;
	htpasswd_list();
};

// ==========

const			init = () => {
	delog();
};

init();
