/*! @preserve
 * bstreeview.js
 * Version: 1.0.0
 * Authors: Sami CHNITER <sami.chniter@gmail.com>
 * Copyright 2020
 * License: Apache License 2.0
 *
 * Project: https://github.com/chniter/bstreeview
 */
; (function ($, window, document, undefined) {
    "use strict";
    /**
     * Default bstreeview  options.
     */
    var pluginName = "bstreeview",
        defaults = {
            expandIcon: "fa fa-angle-down",
            collapseIcon: "fa fa-angle-right",
            downloadIcon: "fa fa-arrow-down",
            indent: 1.25
        };
    /**
     * bstreeview HTML templates.
     */
    var templates = {
        treeview: '<div class="bstreeview"></div>',
        treeviewItem: '<div href="#itemid" class="list-group-item" data-toggle="collapse"></div>',
        treeviewGroupItem: '<div class="list-group collapse" id="itemid"></div>',
        treeviewItemStateIcon: '<i class="state-icon"></i>',
        treeviewItemIcon: '<i class="item-icon"></i>',
        treeviewItemDownloadIcon: '<a class="download-icon"></a>'
    };
    /**
     * BsTreeview Plugin constructor.
     * @param {*} element 
     * @param {*} options 
     */
    function bstreeView(element, options) {
        this.element = element;
        this.itemIdPrefix = element.id + "-item-";
        this.settings = $.extend({}, defaults, options);
        this.init();
    }
    /**
     * Avoid plugin conflict.
     */
    $.extend(bstreeView.prototype, {
        /**
         * bstreeview intialize.
         */
        init: function () {
            this.tree = [];
            this.nodes = [];
            // Retrieve bstreeview Json Data.
            if (this.settings.data) {
            	if (typeof(this.settings.data) == "string") {
            		this.settings.data = $.parseJSON(this.settings.data);
            	}
                this.tree = $.extend(true, [], this.settings.data);
                delete this.settings.data;
            }
            // Set main bstreeview class to element.
            $(this.element).addClass("bstreeview");

            this.initData({ nodes: this.tree });
            var _this = this;
            this.build($(this.element), this.tree, 0);
            // Update angle icon on collapse
            $(this.element).on("click", ".list-group-item", function (sender, args) {
                $(".state-icon", this)
                    .toggleClass(_this.settings.expandIcon)
                    .toggleClass(_this.settings.collapseIcon)
            });
        },
        /**
         * Initialize treeview Data.
         * @param {*} node 
         */
        initData: function (node) {
            if (!node.nodes) return;
            var parent = node;
            var _this = this;
            $.each(node.nodes, function checkStates(index, node) {

                node.nodeId = _this.nodes.length;
                node.parentId = parent.nodeId;
                _this.nodes.push(node);

                if (node.nodes) {
                    _this.initData(node);
                }
            });
        },
        /**
         * Build treeview.
         * @param {*} parentElement 
         * @param {*} nodes 
         * @param {*} depth 
         */
        build: function (parentElement, nodes, depth) {
            var _this = this;
            // Calculate item padding.
            var leftPadding = "1.25rem;";
            if (depth > 0) {
                leftPadding = (_this.settings.indent + depth * _this.settings.indent).toString() + "rem;";
            }
            depth += 1;
            // Add each node and sub-nodes.
            $.each(nodes, function addNodes(id, node) {
                // Main node element.
                var treeItem = $(templates.treeviewItem)
	                .attr("href", "#" + _this.itemIdPrefix + node.nodeId)
	                .attr("style", "padding-left:" + leftPadding);                	
                
                if (node.href) {
                    // add download icon.
                    var treeItemIcon = $(templates.treeviewItemDownloadIcon)
                        .addClass(_this.settings.downloadIcon)
                		.attr("href", node.href)
                		.attr("title", `download ${node.text}`)
                    treeItem.append(treeItemIcon);
                    if (node.img) {
                    	// there is a thumbnail image, save as attribute
                    	treeItem.attr("thumb", node.img)
                    }
                    if (node.id) {
                    	// save primary key of document (for lazy loading of previews)
                    	treeItem.attr("pk", node.id)
                    }
                }

                // Set Expand and Collapse icons.
                if (node.nodes) {
                    var treeItemStateIcon = $(templates.treeviewItemStateIcon)
                        .addClass(_this.settings.collapseIcon);
                    treeItem.append(treeItemStateIcon);
                }
                // set node icon if exist.
                if (node.icon) {
                    var treeItemIcon = $(templates.treeviewItemIcon)
                        .addClass(node.icon);
                    treeItem.append(treeItemIcon);
                }
                // Set node Text.
                treeItem.append(node.text);

                // Add class to node if present
                if (node.class) {
                    treeItem.addClass(node.class);
                }

                // Attach node to parent.
                parentElement.append(treeItem);
                // Build child nodes.
                if (node.nodes) {
                    // Node group item.
                    var treeGroup = $(templates.treeviewGroupItem).attr("id", _this.itemIdPrefix + node.nodeId);
                    if (node.state == 'open')
                    	treeGroup.addClass('open')
                    parentElement.append(treeGroup);
                    _this.build(treeGroup, node.nodes, depth);
                }
            });
        }
    });

    // A really lightweight plugin wrapper around the constructor,
    // preventing against multiple instantiations
    $.fn[pluginName] = function (options) {
        return this.each(function () {
            if (!$.data(this, "plugin_" + pluginName)) {
                $.data(this, "plugin_" +
                    pluginName, new bstreeView(this, options));
            }
        });
    };
})(jQuery, window, document);
