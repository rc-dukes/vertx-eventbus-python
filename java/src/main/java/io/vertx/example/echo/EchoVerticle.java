package io.vertx.example.echo;

import java.util.List;

import io.vertx.core.Promise;
import io.vertx.core.json.JsonObject;
import io.vertx.example.util.VertxStarter;
import io.vertx.ext.bridge.BridgeOptions;
import io.vertx.ext.bridge.PermittedOptions;
import io.vertx.ext.eventbus.bridge.tcp.TcpEventBusBridge;
import io.vertx.reactivex.core.AbstractVerticle;
import io.vertx.reactivex.core.MultiMap;
import io.vertx.reactivex.core.eventbus.EventBus;
import io.vertx.reactivex.core.eventbus.MessageConsumer;

/**
 * a verticle which echos any message send to it as a reply
 * 
 * @author jay
 * @author wf
 */
public class EchoVerticle extends AbstractVerticle {
  public int port = 7001;
  boolean allowExit;

  public EchoVerticle(boolean allowExit) {
    this.allowExit = allowExit;
  }

  public EchoVerticle() {
    this(false);
  }

  public String getHeaderText(MultiMap headers, String indent) {
    String headerText = "";
    for (String name : headers.names()) {
      headerText += indent + name;
      String delim = "";
      List<String> headerParts = headers.getAll(name);
      for (String header : headerParts) {
        headerText += delim + header;
        delim = ",";
      }
      headerText += "\n";
    }
    return headerText;
  }

  @Override
  public void start(Promise<Void> promise) {

    TcpEventBusBridge bridge = TcpEventBusBridge.create(vertx.getDelegate(),
        new BridgeOptions()
            .addInboundPermitted(new PermittedOptions().setAddress("echo"))
            .addOutboundPermitted(new PermittedOptions().setAddress("echo")));

    bridge.listen(port, res -> {
      if (res.succeeded()) {

      } else {
        System.err.println("listen failed - can't start Echo Verticle");
        System.err.println(
            "is there another process listening on port " + port + "?");
        if (allowExit)
          System.exit(1);
      }
    });
    EventBus eb = vertx.eventBus();

    MessageConsumer<JsonObject> consumer = eb.consumer("echo", message -> {
      JsonObject jo = message.body();
      String headerText = getHeaderText(message.headers(), "  ");
      long time = System.nanoTime();

      String msg = String.format(
          "Echo Verticle received:\n%s\nheaders:\n%s\n will reply it back now with received_time timestamp %d...",
          jo, headerText, time);
      System.out.println(msg);
      jo.put("received_time", time);
      message.reply(jo);
    });
    promise.complete();
  }

  // Convenience method so you can run it in your IDE
  public static void main(String[] args) {
    VertxStarter.runClusteredExample(new EchoVerticle(true));
  }
}
