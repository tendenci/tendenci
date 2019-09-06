

var PhotoClient = function(){
/* communicates with Photo API
   basic methods: read; NOT SUPPORTED YET: create, update, delete
   every method takes 2 arguments
   1st argument: object or query string
   2nd argument: callback or object w/ specific callback(s) */

	var self = this;
	var private = {};

	self.read = function(data, callback){
		private.read(data, callback);
	};

	private.read = function(data, callback){
	// read stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/photos.json",
			global: false,
			type: "GET",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};
};
var PhotoNeighborClient = function(){
/* communicates with Photo API
   basic methods: read; NOT SUPPORTED YET: create, update, delete
   every method takes 2 arguments
   1st argument: object or query string
   2nd argument: callback or object w/ specific callback(s) */

	var self = this;
	var private = {};

	self.read = function(data, callback){
		private.read(data, callback);
	};

	private.read = function(data, callback){
	// read stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/photo-neighbors.json",
			global: false,
			type: "GET",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};
};


var StreamClient = function(){
/* communicates with Stream API
   basic methods: create,read,update,delete (CRUD)
   every method takes 2 arguments
   1st argument: object or query string
   2nd argument: callback or object w/ specific callback(s) */

	var self = this;
	var private = {};

	self.read = function(data, callback){
		private.read(data, callback);
	};
	self.create = function(data, callback){
		private.create(data, callback);
	};
	self.update = function(data, callback){
		private.update(data, callback);
	};
	self.delete_ = function(data, callback){
		private.delete_(data, callback);
	};

	private.read = function(data, callback){
	// read stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/streams.json",
			global: false,
			type: "GET",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.create = function(data, callback){
	// create stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/streams.json",
			global: false,
			type: "POST",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.update = function(data, callback){
	// update stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/streams.json",
			global: false,
			type: "PUT",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.delete_ = function(data, callback){
	// delete stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}
		$.ajax({
			url: "/api/streams.json?" + data,
			global: false,
			type: "DELETE",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};
};

var ServiceProfileClient = function(){
/* communicates with Service Profile API
   basic methods: create,read,update,delete (CRUD)
   every method takes 2 arguments
   1st argument: object or query string
   2nd argument: callback or object w/ specific callback(s) */

	var self = this;
	var private = {};

	self.read = function(data, callback){
		private.read(data, callback);
	};
	self.create = function(data, callback){
		private.create(data, callback);
	};
	self.update = function(data, callback){
		private.update(data, callback);
	};
	self.delete_ = function(data, callback){
		private.delete_(data, callback);
	};

	private.read = function(data, callback){
	// read stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/service-profiles.json",
			global: false,
			type: "GET",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.create = function(data, callback){
	// create stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/service-profiles.json",
			global: false,
			type: "POST",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.update = function(data, callback){
	// update stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/service-profiles.json",
			global: false,
			type: "PUT",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.delete_ = function(data, callback){
	// delete stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/service-profiles.json",
			global: false,
			type: "DELETE",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};
};

var ServiceEntryClient = function(){
/* communicates with Service Entry API
   basic methods: create,read,update,delete (CRUD)
   every method takes 2 arguments
   1st argument: object or query string
   2nd argument: callback or object w/ specific callback(s) */

	var self = this;
	var private = {};

	self.read = function(data, callback){
		private.read(data, callback);
	};
	self.create = function(data, callback){
		private.create(data, callback);
	};
	self.update = function(data, callback){
		private.update(data, callback);
	};
	self.delete_ = function(data, callback){
		private.delete_(data, callback);
	};

	private.read = function(data, callback){
	// read stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/service-entries.json",
			global: false,
			type: "GET",
			data: data,
			contentType: "*/json; charset=utf-8",
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.create = function(data, callback){
	// create stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/service-entries.json",
			global: false,
			type: "POST",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.update = function(data, callback){
	// update stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/service-entries.json",
			global: false,
			type: "PUT",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.delete_ = function(data, callback){
	// delete stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/service-entries.json",
			global: false,
			type: "DELETE",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};
};

var DashboardClient = function(){
/* communicates with Service Entry API
   basic methods: create,read,update,delete (CRUD)
   every method takes 2 arguments
   1st argument: object or query string
   2nd argument: callback or object w/ specific callback(s) */

	var self = this;
	var private = {};

	self.read = function(data, callback){
		private.read(data, callback);
	};
	self.create = function(data, callback){
		private.create(data, callback);
	};

	private.read = function(data, callback){
	// read stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/dashboard.json",
			global: false,
			type: "GET",
			data: data,
			contentType: "*/json; charset=utf-8",
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};

	private.create = function(data, callback){
	// create stream
		var error = function(){};
		var success = function(){};
		var complete = function(){};

		if(callback && typeof(callback)=="function"){
			success = callback;
		}
		else if(callback && typeof(callback)=="object"){
			if(typeof(callback.error)=="function") error = callback.error;
			if(typeof(callback.success)=="function") success = callback.success;
			if(typeof(callback.complete)=="function") complete = callback.complete;
		}

		$.ajax({
			url: "/api/dashboard.json",
			global: false,
			type: "POST",
			data: data,
			dataType: "json",
			cache: false,
			error: error, // error(xhr, status, error)
			success: success, // success(data, status, xhr)
			complete: complete // complete(xhr, status)
		});
	};
};
