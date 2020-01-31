package io.vertx.example.reactivex.eventbus.pubsub;

import io.vertx.reactivex.core.AbstractVerticle;
import io.vertx.reactivex.core.eventbus.EventBus;
import io.vertx.core.Promise;
import io.vertx.example.util.VertxStarter;

/*
 * @author <a href="http://tfox.org">Tim Fox</a>
 * https://raw.githubusercontent.com/vert-x3/vertx-examples/master/rxjava-2-examples/src/main/java/io/vertx/example/reactivex/eventbus/pubsub/Sender.java
 */
public class Sender extends AbstractVerticle {


  @Override
  public void start(Promise<Void> promise) throws Exception {
    EventBus eb = vertx.eventBus();
    // Send a message every second
    vertx.setPeriodic(1000, v -> eb.publish("news-feed", "Some news!"));
    promise.complete();
  }
  
  // Convenience method so you can run it in your IDE
  public static void main(String[] args) {
    VertxStarter.runClusteredExample(new Sender());
  }
}
