/** @odoo-module **/

import publicWidget from 'web.public.widget';
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.WishVoting = publicWidget.Widget.extend({
    selector: '.wish-grid',
    events: {
        'click .vote-btn': '_onVoteClick',
    },

    _onVoteClick: async function (ev) {
        ev.preventDefault();
        const btn = $(ev.currentTarget);
        const wishId = btn.data('wish-id');
        const countSpan = btn.find('.vote-count');

        btn.addClass('voted');
        try {
            const data = await jsonrpc('/community/wish/vote', {
                wish_id: wishId,
            });
            if (data.new_count !== undefined) {
                countSpan.text(data.new_count);
                const icon = btn.find('i');
                icon.addClass('fa-beat');
                setTimeout(() => icon.removeClass('fa-beat'), 1000);
            }
        } catch (error) {
            btn.removeClass('voted');
        }
    },
});

