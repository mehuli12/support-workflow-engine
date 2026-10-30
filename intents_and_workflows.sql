USE support_engine;

INSERT INTO intents (intent_id, intent_name, description, target_resolution_hours) VALUES
(1, 'order_status',        'Customer asks where their order is',             4),
(2, 'delivery_delay',      'Order is late or stuck in transit',              24),
(3, 'refund_request',      'Customer wants money back for an order',         48),
(4, 'billing_dispute',     'Customer disputes a charge on their account',    48),
(5, 'password_reset',      'Customer cannot log in or needs a new password', 1),
(6, 'account_access',      'Account locked or access problem',               4),
(7, 'product_defect',      'Product arrived broken or not working',          72),
(8, 'cancel_subscription', 'Customer wants to cancel a subscription',        24),
(9, 'general_enquiry',     'Anything that does not fit another intent',      24);

INSERT INTO workflows (workflow_id, intent_id, workflow_name, config_file, is_self_service) VALUES
(1, 1, 'Order Status Check',      'workflows/order_status.yaml',        TRUE),
(2, 2, 'Delivery Delay Handler',  'workflows/delivery_delay.yaml',      TRUE),
(3, 3, 'Refund Request',          'workflows/refund_request.yaml',      FALSE),
(4, 4, 'Billing Dispute',         'workflows/billing_dispute.yaml',     FALSE),
(5, 5, 'Password Reset',          'workflows/password_reset.json',      TRUE),
(6, 6, 'Account Access Recovery', 'workflows/account_access.json',      FALSE),
(7, 7, 'Product Defect Claim',    'workflows/product_defect.json',      FALSE),
(8, 8, 'Cancel Subscription',     'workflows/cancel_subscription.json', TRUE),
(9, 9, 'General Enquiry',         'workflows/general_enquiry.json',     FALSE);
