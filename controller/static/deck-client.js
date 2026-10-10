/*
 * Deck bridge for the PP1 remote controller.
 * Injected by controller/app.py when the deck is served through FastAPI.
 * Connects to the controller WebSocket and drives Reveal.js.
 * Kept separate from the presentation code in ../presentation.
 */
(function () {
	"use strict";

	if (typeof Reveal === "undefined") return;

	var socket = null;
	var reconnectDelay = 1000;

	function socketUrl() {
		var protocol = location.protocol === "https:" ? "wss:" : "ws:";
		return protocol + "//" + location.host + "/ws?role=deck";
	}

	function currentState() {
		var indices = Reveal.getIndices();
		return {
			type: "state",
			indexh: indices.h,
			indexv: indices.v,
			current: indices.h + 1,
			total: Reveal.getHorizontalSlides().length,
		};
	}

	function sendState() {
		if (socket && socket.readyState === WebSocket.OPEN) {
			socket.send(JSON.stringify(currentState()));
		}
	}

	function apply(action) {
		switch (action) {
			case "next":
				Reveal.next();
				break;
			case "prev":
				Reveal.prev();
				break;
			case "home":
				Reveal.slide(0);
				break;
			case "end":
				Reveal.slide(Reveal.getHorizontalSlides().length - 1);
				break;
			default:
				break;
		}
	}

	function connect() {
		socket = new WebSocket(socketUrl());

		socket.addEventListener("open", function () {
			reconnectDelay = 1000;
			sendState();
		});

		socket.addEventListener("message", function (event) {
			var message;
			try {
				message = JSON.parse(event.data);
			} catch (error) {
				return;
			}
			if (message && message.type === "command") {
				apply(message.action);
			}
		});

		socket.addEventListener("close", function () {
			window.setTimeout(connect, reconnectDelay);
			reconnectDelay = Math.min(reconnectDelay * 2, 8000);
		});

		socket.addEventListener("error", function () {
			socket.close();
		});
	}

	function boot() {
		Reveal.on("ready", sendState);
		Reveal.on("slidechanged", sendState);
		sendState();
		connect();
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", boot);
	} else {
		boot();
	}
})();
