/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/email.coffee");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./src/email.coffee":
/*!**************************!*\
  !*** ./src/email.coffee ***!
  \**************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
eval("\n\nvar _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if (\"value\" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();\n\nfunction _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError(\"Cannot call a class as a function\"); } }\n\n// DOCUMENT READY ENTRY POINT\nvar EmailController;\n\ndocument.addEventListener(\"DOMContentLoaded\", function () {\n  var controller;\n  console.debug(\"*** SENAITE.IMPRESS::DOMContentLoaded: --> Loading Email Controller\");\n  controller = new EmailController();\n  return controller.initialize();\n});\n\nEmailController = function () {\n  function EmailController() {\n    _classCallCheck(this, EmailController);\n\n    this.bind_eventhandler = this.bind_eventhandler.bind(this);\n    this.is_visible = this.is_visible.bind(this);\n    this.toggle_attachments_container = this.toggle_attachments_container.bind(this);\n    this.update_size_info = this.update_size_info.bind(this);\n    this.on_add_attachments_click = this.on_add_attachments_click.bind(this);\n    this.on_attachments_select = this.on_attachments_select.bind(this);\n    this.bind_eventhandler();\n    return this;\n  }\n\n  _createClass(EmailController, [{\n    key: \"initialize\",\n    value: function initialize() {\n      console.debug(\"senaite.impress:Email::initialize\");\n      // Initialize overlays\n      return this.init_overlays();\n    }\n  }, {\n    key: \"init_overlays\",\n    value: function init_overlays() {\n      /*\n       * Initialize all overlays for later loading\n       *\n       */\n      console.debug(\"senaite.impress:Email::init_overlays\");\n      return $(\"a.attachment-link,a.report-link\").prepOverlay({\n        subtype: \"iframe\",\n        config: {\n          closeOnClick: true,\n          closeOnEsc: true,\n          onLoad: function onLoad(event) {\n            var iframe, overlay;\n            overlay = this.getOverlay();\n            iframe = overlay.find(\"iframe\");\n            return iframe.css({\n              \"background\": \"white\"\n            });\n          }\n        }\n      });\n    }\n  }, {\n    key: \"bind_eventhandler\",\n    value: function bind_eventhandler() {\n      /*\n       * Binds callbacks on elements\n       *\n       * N.B. We attach all the events to the body and refine the selector to\n       * delegate the event: https://learn.jquery.com/events/event-delegation/\n       *\n       */\n      console.debug(\"senaite.impress::bind_eventhandler\");\n      // Toggle additional attachments visibility\n      $(\"body\").on(\"click\", \"#add-attachments\", this.on_add_attachments_click);\n      // Select/deselect additional attachments\n      return $(\"body\").on(\"change\", \".attachments input[type='checkbox']\", this.on_attachments_select);\n    }\n  }, {\n    key: \"get_base_url\",\n    value: function get_base_url() {\n      /*\n       * Calculate the current base url\n       */\n      return document.URL.split(\"?\")[0];\n    }\n  }, {\n    key: \"get_api_url\",\n    value: function get_api_url(endpoint) {\n      /*\n       * Build API URL for the given endpoint\n       * @param {string} endpoint\n       * @returns {string}\n       */\n      var base_url;\n      base_url = this.get_base_url();\n      return base_url + \"/\" + endpoint;\n    }\n  }, {\n    key: \"ajax_fetch\",\n    value: function ajax_fetch(endpoint, init) {\n      /*\n       * Call resource on the server\n       * @param {string} endpoint\n       * @param {object} options\n       * @returns {Promise}\n       */\n      var request, url;\n      url = this.get_api_url(endpoint);\n      if (init == null) {\n        init = {};\n      }\n      if (init.method == null) {\n        init.method = \"POST\";\n      }\n      if (init.credentials == null) {\n        init.credentials = \"include\";\n      }\n      if (init.body == null) {\n        init.body = null;\n      }\n      if (init.header == null) {\n        init.header = null;\n      }\n      console.info(\"Email::fetch:endpoint=\" + endpoint + \" init=\", init);\n      request = new Request(url, init);\n      return fetch(request).then(function (response) {\n        return response.json();\n      });\n    }\n  }, {\n    key: \"is_visible\",\n    value: function is_visible(element) {\n      /*\n       * Checks if the element is visible\n       */\n      if ($(element).css(\"display\") === \"none\") {\n        return false;\n      }\n      return true;\n    }\n  }, {\n    key: \"toggle_attachments_container\",\n    value: function toggle_attachments_container() {\n      var toggle = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;\n\n      /*\n       * Toggle the visibility of the attachments container\n       */\n      var button, container, visible;\n      button = $(\"#add-attachments\");\n      container = $(\"#additional-attachments-container\");\n      visible = this.is_visible(container);\n      if (toggle !== null) {\n        visible = toggle ? false : true;\n      }\n      if (visible === true) {\n        container.hide();\n        return button.text(\"+\");\n      } else {\n        container.show();\n        return button.text(\"-\");\n      }\n    }\n  }, {\n    key: \"update_size_info\",\n    value: function update_size_info(data) {\n      var unit;\n      /*\n       * Update the total size of the selected attachments\n       */\n      if (!data) {\n        console.warn(\"No valid size information: \", data);\n        return null;\n      }\n      unit = \"kB\";\n      $(\"#attachment-files\").text(\"\" + data.files);\n      if (data.limit_exceeded) {\n        $(\"#email-size\").addClass(\"text-danger\");\n        $(\"#email-size\").text(data.size + \" \" + unit + \" > \" + data.limit + \" \" + unit);\n        return $(\"input[name='send']\").prop(\"disabled\", true);\n      } else {\n        $(\"#email-size\").removeClass(\"text-danger\");\n        $(\"#email-size\").text(data.size + \" \" + unit);\n        return $(\"input[name='send']\").prop(\"disabled\", false);\n      }\n    }\n  }, {\n    key: \"on_add_attachments_click\",\n    value: function on_add_attachments_click(event) {\n      console.debug(\"°°° Email::on_add_attachments_click\");\n      event.preventDefault();\n      return this.toggle_attachments_container();\n    }\n  }, {\n    key: \"on_attachments_select\",\n    value: function on_attachments_select(event) {\n      var _this = this;\n\n      var form, form_data, init;\n      console.debug(\"°°° Email::on_attachments_select\");\n      // extract the form data\n      form = $(\"#send_email_form\");\n      // form.serialize does not include file attachments\n      // form_data = form.serialize()\n      form_data = new FormData(form[0]);\n      init = {\n        body: form_data\n      };\n      return this.ajax_fetch(\"recalculate_size\", init).then(function (data) {\n        return _this.update_size_info(data);\n      });\n    }\n  }]);\n\n  return EmailController;\n}();//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zcmMvZW1haWwuY29mZmVlLmpzIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vLy4vc3JjL2VtYWlsLmNvZmZlZT85NjM2Il0sInNvdXJjZXNDb250ZW50IjpbIiMgRE9DVU1FTlQgUkVBRFkgRU5UUlkgUE9JTlRcbmRvY3VtZW50LmFkZEV2ZW50TGlzdGVuZXIgXCJET01Db250ZW50TG9hZGVkXCIsIC0+XG4gIGNvbnNvbGUuZGVidWcgXCIqKiogU0VOQUlURS5JTVBSRVNTOjpET01Db250ZW50TG9hZGVkOiAtLT4gTG9hZGluZyBFbWFpbCBDb250cm9sbGVyXCJcbiAgY29udHJvbGxlciA9IG5ldyBFbWFpbENvbnRyb2xsZXIoKVxuICBjb250cm9sbGVyLmluaXRpYWxpemUoKVxuXG5cbmNsYXNzIEVtYWlsQ29udHJvbGxlclxuXG4gIGNvbnN0cnVjdG9yOiAoKSAtPlxuICAgIEBiaW5kX2V2ZW50aGFuZGxlcigpXG4gICAgcmV0dXJuIEBcblxuXG4gIGluaXRpYWxpemU6IC0+XG4gICAgY29uc29sZS5kZWJ1ZyBcInNlbmFpdGUuaW1wcmVzczpFbWFpbDo6aW5pdGlhbGl6ZVwiXG4gICAgIyBJbml0aWFsaXplIG92ZXJsYXlzXG4gICAgQGluaXRfb3ZlcmxheXMoKVxuXG5cbiAgaW5pdF9vdmVybGF5czogLT5cbiAgICAjIyNcbiAgICAgKiBJbml0aWFsaXplIGFsbCBvdmVybGF5cyBmb3IgbGF0ZXIgbG9hZGluZ1xuICAgICAqXG4gICAgIyMjXG4gICAgY29uc29sZS5kZWJ1ZyBcInNlbmFpdGUuaW1wcmVzczpFbWFpbDo6aW5pdF9vdmVybGF5c1wiXG5cbiAgICAkKFwiYS5hdHRhY2htZW50LWxpbmssYS5yZXBvcnQtbGlua1wiKS5wcmVwT3ZlcmxheVxuICAgICAgc3VidHlwZTogXCJpZnJhbWVcIlxuICAgICAgY29uZmlnOlxuICAgICAgICBjbG9zZU9uQ2xpY2s6IHllc1xuICAgICAgICBjbG9zZU9uRXNjOiB5ZXNcbiAgICAgICAgb25Mb2FkOiAoZXZlbnQpIC0+XG4gICAgICAgICAgb3ZlcmxheSA9IHRoaXMuZ2V0T3ZlcmxheSgpXG4gICAgICAgICAgaWZyYW1lID0gb3ZlcmxheS5maW5kIFwiaWZyYW1lXCJcbiAgICAgICAgICBpZnJhbWUuY3NzXG4gICAgICAgICAgICBcImJhY2tncm91bmRcIjogXCJ3aGl0ZVwiXG5cblxuICBiaW5kX2V2ZW50aGFuZGxlcjogPT5cbiAgICAjIyNcbiAgICAgKiBCaW5kcyBjYWxsYmFja3Mgb24gZWxlbWVudHNcbiAgICAgKlxuICAgICAqIE4uQi4gV2UgYXR0YWNoIGFsbCB0aGUgZXZlbnRzIHRvIHRoZSBib2R5IGFuZCByZWZpbmUgdGhlIHNlbGVjdG9yIHRvXG4gICAgICogZGVsZWdhdGUgdGhlIGV2ZW50OiBodHRwczovL2xlYXJuLmpxdWVyeS5jb20vZXZlbnRzL2V2ZW50LWRlbGVnYXRpb24vXG4gICAgICpcbiAgICAjIyNcbiAgICBjb25zb2xlLmRlYnVnIFwic2VuYWl0ZS5pbXByZXNzOjpiaW5kX2V2ZW50aGFuZGxlclwiXG5cbiAgICAjIFRvZ2dsZSBhZGRpdGlvbmFsIGF0dGFjaG1lbnRzIHZpc2liaWxpdHlcbiAgICAkKFwiYm9keVwiKS5vbiBcImNsaWNrXCIsIFwiI2FkZC1hdHRhY2htZW50c1wiLCBAb25fYWRkX2F0dGFjaG1lbnRzX2NsaWNrXG5cbiAgICAjIFNlbGVjdC9kZXNlbGVjdCBhZGRpdGlvbmFsIGF0dGFjaG1lbnRzXG4gICAgJChcImJvZHlcIikub24gXCJjaGFuZ2VcIiwgXCIuYXR0YWNobWVudHMgaW5wdXRbdHlwZT0nY2hlY2tib3gnXVwiLCBAb25fYXR0YWNobWVudHNfc2VsZWN0XG5cblxuICBnZXRfYmFzZV91cmw6IC0+XG4gICAgIyMjXG4gICAgICogQ2FsY3VsYXRlIHRoZSBjdXJyZW50IGJhc2UgdXJsXG4gICAgIyMjXG4gICAgcmV0dXJuIGRvY3VtZW50LlVSTC5zcGxpdChcIj9cIilbMF1cblxuXG4gIGdldF9hcGlfdXJsOiAoZW5kcG9pbnQpIC0+XG4gICAgIyMjXG4gICAgICogQnVpbGQgQVBJIFVSTCBmb3IgdGhlIGdpdmVuIGVuZHBvaW50XG4gICAgICogQHBhcmFtIHtzdHJpbmd9IGVuZHBvaW50XG4gICAgICogQHJldHVybnMge3N0cmluZ31cbiAgICAjIyNcbiAgICBiYXNlX3VybCA9IEBnZXRfYmFzZV91cmwoKVxuICAgIHJldHVybiBcIiN7YmFzZV91cmx9LyN7ZW5kcG9pbnR9XCJcblxuXG4gIGFqYXhfZmV0Y2g6IChlbmRwb2ludCwgaW5pdCkgLT5cbiAgICAjIyNcbiAgICAgKiBDYWxsIHJlc291cmNlIG9uIHRoZSBzZXJ2ZXJcbiAgICAgKiBAcGFyYW0ge3N0cmluZ30gZW5kcG9pbnRcbiAgICAgKiBAcGFyYW0ge29iamVjdH0gb3B0aW9uc1xuICAgICAqIEByZXR1cm5zIHtQcm9taXNlfVxuICAgICMjI1xuXG4gICAgdXJsID0gQGdldF9hcGlfdXJsIGVuZHBvaW50XG5cbiAgICBpbml0ID89IHt9XG4gICAgaW5pdC5tZXRob2QgPz0gXCJQT1NUXCJcbiAgICBpbml0LmNyZWRlbnRpYWxzID89IFwiaW5jbHVkZVwiXG4gICAgaW5pdC5ib2R5ID89IG51bGxcbiAgICBpbml0LmhlYWRlciA/PSBudWxsXG5cbiAgICBjb25zb2xlLmluZm8gXCJFbWFpbDo6ZmV0Y2g6ZW5kcG9pbnQ9I3tlbmRwb2ludH0gaW5pdD1cIixpbml0XG4gICAgcmVxdWVzdCA9IG5ldyBSZXF1ZXN0KHVybCwgaW5pdClcbiAgICByZXR1cm4gZmV0Y2gocmVxdWVzdCkudGhlbiAocmVzcG9uc2UpIC0+XG4gICAgICByZXR1cm4gcmVzcG9uc2UuanNvbigpXG5cblxuICBpc192aXNpYmxlOiAoZWxlbWVudCkgPT5cbiAgICAjIyNcbiAgICAgKiBDaGVja3MgaWYgdGhlIGVsZW1lbnQgaXMgdmlzaWJsZVxuICAgICMjI1xuICAgIGlmICQoZWxlbWVudCkuY3NzKFwiZGlzcGxheVwiKSBpcyBcIm5vbmVcIlxuICAgICAgcmV0dXJuIG5vXG4gICAgcmV0dXJuIHllc1xuXG5cbiAgdG9nZ2xlX2F0dGFjaG1lbnRzX2NvbnRhaW5lcjogKHRvZ2dsZT1udWxsKSA9PlxuICAgICMjI1xuICAgICAqIFRvZ2dsZSB0aGUgdmlzaWJpbGl0eSBvZiB0aGUgYXR0YWNobWVudHMgY29udGFpbmVyXG4gICAgIyMjXG5cbiAgICBidXR0b24gPSAkKFwiI2FkZC1hdHRhY2htZW50c1wiKVxuICAgIGNvbnRhaW5lciA9ICQoXCIjYWRkaXRpb25hbC1hdHRhY2htZW50cy1jb250YWluZXJcIilcblxuICAgIHZpc2libGUgPSBAaXNfdmlzaWJsZSBjb250YWluZXJcbiAgICBpZiB0b2dnbGUgaXNudCBudWxsXG4gICAgICB2aXNpYmxlID0gaWYgdG9nZ2xlIHRoZW4gbm8gZWxzZSB5ZXNcblxuICAgIGlmIHZpc2libGUgaXMgeWVzXG4gICAgICBjb250YWluZXIuaGlkZSgpXG4gICAgICBidXR0b24udGV4dCBcIitcIlxuICAgIGVsc2VcbiAgICAgIGNvbnRhaW5lci5zaG93KClcbiAgICAgIGJ1dHRvbi50ZXh0IFwiLVwiXG5cblxuICB1cGRhdGVfc2l6ZV9pbmZvOiAoZGF0YSkgPT5cbiAgICAjIyNcbiAgICAgKiBVcGRhdGUgdGhlIHRvdGFsIHNpemUgb2YgdGhlIHNlbGVjdGVkIGF0dGFjaG1lbnRzXG4gICAgIyMjXG4gICAgaWYgbm90IGRhdGFcbiAgICAgIGNvbnNvbGUud2FybiBcIk5vIHZhbGlkIHNpemUgaW5mb3JtYXRpb246IFwiLCBkYXRhXG4gICAgICByZXR1cm4gbnVsbFxuXG4gICAgdW5pdCA9IFwia0JcIlxuICAgICQoXCIjYXR0YWNobWVudC1maWxlc1wiKS50ZXh0IFwiI3tkYXRhLmZpbGVzfVwiXG5cbiAgICBpZiBkYXRhLmxpbWl0X2V4Y2VlZGVkXG4gICAgICAkKFwiI2VtYWlsLXNpemVcIikuYWRkQ2xhc3MgXCJ0ZXh0LWRhbmdlclwiXG4gICAgICAkKFwiI2VtYWlsLXNpemVcIikudGV4dCBcIiN7ZGF0YS5zaXplfSAje3VuaXR9ID4gI3tkYXRhLmxpbWl0fSAje3VuaXR9XCJcbiAgICAgICQoXCJpbnB1dFtuYW1lPSdzZW5kJ11cIikucHJvcCBcImRpc2FibGVkXCIsIG9uXG4gICAgZWxzZVxuICAgICAgJChcIiNlbWFpbC1zaXplXCIpLnJlbW92ZUNsYXNzIFwidGV4dC1kYW5nZXJcIlxuICAgICAgJChcIiNlbWFpbC1zaXplXCIpLnRleHQgXCIje2RhdGEuc2l6ZX0gI3t1bml0fVwiXG4gICAgICAkKFwiaW5wdXRbbmFtZT0nc2VuZCddXCIpLnByb3AgXCJkaXNhYmxlZFwiLCBvZmZcblxuXG4gIG9uX2FkZF9hdHRhY2htZW50c19jbGljazogKGV2ZW50KSA9PlxuICAgIGNvbnNvbGUuZGVidWcgXCLCsMKwwrAgRW1haWw6Om9uX2FkZF9hdHRhY2htZW50c19jbGlja1wiXG4gICAgZXZlbnQucHJldmVudERlZmF1bHQoKVxuICAgIEB0b2dnbGVfYXR0YWNobWVudHNfY29udGFpbmVyKClcblxuXG4gIG9uX2F0dGFjaG1lbnRzX3NlbGVjdDogKGV2ZW50KSA9PlxuICAgIGNvbnNvbGUuZGVidWcgXCLCsMKwwrAgRW1haWw6Om9uX2F0dGFjaG1lbnRzX3NlbGVjdFwiXG5cbiAgICAjIGV4dHJhY3QgdGhlIGZvcm0gZGF0YVxuICAgIGZvcm0gPSAkKFwiI3NlbmRfZW1haWxfZm9ybVwiKVxuICAgICMgZm9ybS5zZXJpYWxpemUgZG9lcyBub3QgaW5jbHVkZSBmaWxlIGF0dGFjaG1lbnRzXG4gICAgIyBmb3JtX2RhdGEgPSBmb3JtLnNlcmlhbGl6ZSgpXG4gICAgZm9ybV9kYXRhID0gbmV3IEZvcm1EYXRhKGZvcm1bMF0pXG5cbiAgICBpbml0ID1cbiAgICAgIGJvZHk6IGZvcm1fZGF0YVxuICAgIEBhamF4X2ZldGNoIFwicmVjYWxjdWxhdGVfc2l6ZVwiLCBpbml0XG4gICAgLnRoZW4gKGRhdGEpID0+XG4gICAgICBAdXBkYXRlX3NpemVfaW5mbyBkYXRhXG4iXSwibWFwcGluZ3MiOiI7Ozs7Ozs7QUFBQTtBQUNBO0FBQUE7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUhBO0FBQ0E7QUFLQTtBQUVBO0FBQUE7QUFDQTtBQTZCQTtBQXdEQTtBQVNBO0FBb0JBO0FBcUJBO0FBTUE7QUE3SUE7QUFDQTtBQUZBO0FBQ0E7QUFIQTtBQUFBO0FBQUE7QUFRQTs7QUFFQTtBQUhBO0FBUEE7QUFBQTtBQUFBOzs7OztBQWtCQTtBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUpBO0FBRkE7QUFGQTtBQVJBO0FBYkE7QUFBQTtBQUFBOzs7Ozs7OztBQXdDQTs7QUFHQTs7QUFHQTtBQWRBO0FBaENBO0FBQUE7QUFBQTs7OztBQXFEQTtBQUpBO0FBakRBO0FBQUE7QUFBQTs7Ozs7O0FBOERBO0FBQUE7QUFDQTtBQVBBO0FBeERBO0FBQUE7QUFBQTs7Ozs7OztBQTBFQTtBQUFBOztBQUVBOzs7QUFDQTs7O0FBQ0E7OztBQUNBOzs7QUFDQTs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQURBO0FBbEJBO0FBbEVBO0FBQUE7QUFBQTs7OztBQTRGQTtBQUNBOztBQUNBO0FBTkE7QUF4RkE7QUFBQTtBQUFBO0FBaUdBO0FBQ0E7Ozs7QUFJQTtBQUFBO0FBQ0E7QUFFQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBO0FBRkE7QUFJQTtBQUNBOztBQWpCQTtBQWpHQTtBQUFBO0FBQUE7QUF5SEE7Ozs7QUFBQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBSEE7QUFLQTtBQUNBO0FBQ0E7O0FBbEJBO0FBckhBO0FBQUE7QUFBQTtBQTJJQTtBQUNBO0FBQ0E7QUFIQTtBQTFJQTtBQUFBO0FBQUE7QUFnSkE7QUFDQTtBQUFBO0FBQUE7O0FBR0E7OztBQUdBO0FBRUE7QUFDQTtBQUFBO0FBQ0E7QUFFQTtBQUZBO0FBWEE7QUFoSkE7QUFDQTtBQURBO0FBQUEiLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./src/email.coffee\n");

/***/ })

/******/ });