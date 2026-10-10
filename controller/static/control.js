/*
 * Mobile control panel client.
 * Sends slide commands to the controller and shows the current slide.
 */
(function () {
	"use strict";

	var statusEl = document.getElementById("status");
	var currentEl = document.getElementById("current");
	var totalEl = document.getElementById("total");

	var socket = null;
	var reconnectDelay = 1000;

	function setStatus(text, state) {
		if (!statusEl) return;
		statusEl.textContent = text;
		statusEl.dataset.state = state;
	}

	function send(action) {
		if (socket && socket.readyState === WebSocket.OPEN) {
			socket.send(JSON.stringify({ type: "command", action: action }));
		}
	}

	function bind(id, action) {
		var el = document.getElementById(id);
		if (!el) return;
		el.addEventListener("click", function () {
			send(action);
		});
	}

	function connect() {
		var protocol = location.protocol === "https:" ? "wss:" : "ws:";
		socket = new WebSocket(protocol + "//" + location.host + "/ws?role=control");

		socket.addEventListener("open", function () {
			reconnectDelay = 1000;
			setStatus("Conectado", "online");
		});

		socket.addEventListener("message", function (event) {
			var message;
			try {
				message = JSON.parse(event.data);
			} catch (error) {
				return;
			}
			if (message && message.type === "state") {
				if (currentEl) currentEl.textContent = message.current;
				if (totalEl) totalEl.textContent = message.total;
			}
		});

		socket.addEventListener("close", function () {
			setStatus("Sin conexión — reintentando…", "offline");
			window.setTimeout(connect, reconnectDelay);
			reconnectDelay = Math.min(reconnectDelay * 2, 8000);
		});

		socket.addEventListener("error", function () {
			socket.close();
		});
	}

	bind("prev", "prev");
	bind("next", "next");
	bind("home", "home");
	bind("end", "end");

	connect();
})();
