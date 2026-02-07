odoo.define('wuchang_community_campaign.campaign', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.WuchangCampaign = publicWidget.Widget.extend({
        selector: '.container',
        start: function () {
            this._renderWishTree();
            this._renderVoting();
            this._renderTransparency();
        },
        _renderWishTree: function () {
            var el = this.$('.wish-tree');
            if (el.length) {
                el.text('Wish Tree is ready. Submit wishes to grow the tree.');
            }
        },
        _renderVoting: function () {
            var el = this.$('#vote-panel');
            if (el.length) {
                el.text('Voting panel initialized.');
            }
        },
        _renderTransparency: function () {
            var el = this.$('#transparency-dashboard');
            if (el.length) {
                el.text('Transparency dashboard online.');
            }
        }
    });
});

