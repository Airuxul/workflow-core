# -*- coding: utf-8 -*-
from .base_trigger_flow import TriggerWorkflow

class WebhookTriggerWorkflow(TriggerWorkflow):
    """
    Webhook触发器，收到HTTP POST请求时触发。
    需设置webhook_port。
    """
    webhook_port = 8000
    def run(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer
        class Handler(BaseHTTPRequestHandler):
            def do_POST(inner_self):
                self.will_trigger = True
        server = HTTPServer(('0.0.0.0', self.webhook_port), Handler)
        self.log(f"Webhook触发器监听端口: {self.webhook_port}")
        TriggerWorkflow.run(self)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.log("Webhook触发器已停止") 
    
    def update_trigger(self):
        pass