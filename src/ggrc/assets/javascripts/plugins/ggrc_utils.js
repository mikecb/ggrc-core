/*!
    Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
    Created By: ivan@reciprocitylabs.com
    Maintained By: ivan@reciprocitylabs.com
*/
(function($, GGRC) {
  GGRC.Utils = {
    getPickerElement: function (picker) {
      return _.find(_.values(picker), function (val) {
        if (val instanceof Node) {
          return /picker\-dialog/.test(val.className);
        }
        return false;
      });
    },
    download: function (filename, text) {
      var element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      element.setAttribute('download', filename);
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    },
    export_request: function (request) {
      return $.ajax({
        type: "POST",
        dataType: "text",
        headers: $.extend({
          "Content-Type": "application/json",
          "X-export-view": "blocks",
          "X-requested-by": "gGRC"
        }, request.headers || {}),
        url: "/_service/export_csv",
        data: JSON.stringify(request.data || {})
      });
    },
    is_mapped: function (target, destination) {
      var table_plural = CMS.Models[destination.type].table_plural,
          bindings = target.get_binding((target.has_binding(table_plural) ? "" : "related_") + table_plural);

      if (bindings && bindings.list && bindings.list.length) {
        return _.find(bindings.list, function (item) {
          return item.instance.id === destination.id;
        });
      }
      if (target.objects && target.objects.length) {
        return _.find(target.objects, function (item) {
          return item.id === destination.id && item.type === destination.type;
        });
      }
    },
    allowed_to_map: function (source, target, options) {
      var can_map = false,
          target_type, source_type;

      target_type = target instanceof can.Model ? target.constructor.shortName
                                                : (target.type || target);
      source_type = source.constructor.shortName || source;
      target_context = target.context && target.context.id;
      source_context = source.context && source.context.id;
      create_contexts = GGRC.permissions.create && GGRC.permissions.create.Relationship && GGRC.permissions.create.Relationship.contexts;

      can_map = Permission.is_allowed_for("update", source) || source_type === "Person" || _.contains(create_contexts, source_context);
      if (target instanceof can.Model) {
        can_map = can_map && (Permission.is_allowed_for("update", target) || target_type === "Person" || _.contains(create_contexts, target_context));
      }
      return can_map;
    }
  };
})(jQuery, window.GGRC = window.GGRC || {});
