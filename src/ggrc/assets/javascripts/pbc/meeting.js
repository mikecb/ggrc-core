/*
 * Copyright (C) 2013 Google Inc., authors, and contributors <see AUTHORS file>
 * Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 * Created By:
 * Maintained By:
 */

//= require can.jquery-all
//= require models/cacheable

can.Model.Cacheable("CMS.Models.Meeting", {
  root_collections : "meetings"
  , root_object : "meeting"
  /*
  Meetings are not implemented on the GGRC server yet.
  , findAll : "GET /api/meetings"
  , create : "POST /api/meetings"
  , update : "PUT /api/meetings/{id}"
  , destroy : "DELETE /api/meetings/{id}"
  */
  , attributes : {
    response : "CMS.Models.Response.stub"
  }
}, {
  init : function () {
      this._super && this._super.apply(this, arguments);
      // this.bind("change", function(ev, attr, how, newVal, oldVal) {
      //     var obj;
      //     if(obj = CMS.Models.ObjectDocument.findInCacheById(this.id) && attr !== "id") {
      //         obj.attr(attr, newVal);
      //     }
      // });

      var that = this;

      this.each(function(value, name) {
        if (value === null)
          that.removeAttr(name);
      });
  }

});