package io.vertx.example.echo;

import io.vertx.core.Future;
import io.vertx.core.json.JsonObject;
import io.vertx.example.util.VertxStarter;
import io.vertx.ext.bridge.BridgeOptions;
import io.vertx.ext.bridge.PermittedOptions;
import io.vertx.ext.eventbus.bridge.tcp.TcpEventBusBridge;
import io.vertx.reactivex.core.AbstractVerticle;
import io.vertx.reactivex.core.eventbus.EventBus;
import io.vertx.reactivex.core.eventbus.MessageConsumer;

/**
 * a verticle which echos any message send to it as a reply
 * @author jay
 * @author wf
 */
public class EchoVerticle extends AbstractVerticle {

  @Override
  public void start(Future<Void> fut) {
    
    TcpEventBusBridge bridge = TcpEventBusBridge.create(vertx.getDelegate(),
        new BridgeOptions()
            .addInboundPermitted(new PermittedOptions().setAddress("echo"))
            .addOutboundPermitted(new PermittedOptions().setAddress("echo")));

    bridge.listen(7001, res -> {
      if (res.succeeded()) {

      } else {
        System.err.println("listen failed - can't start Echo Verticle");
        System.exit(1);
      }
    });
    EventBus eb = vertx.eventBus();

    MessageConsumer<JsonObject> consumer = eb.consumer("echo", message -> {
      message.reply(message.body());
    });

  }
  
  // Convenience method so you can run it in your IDE
  public static void main(String[] args) {
    VertxStarter.runClusteredExample(new EchoVerticle());
  }
}
