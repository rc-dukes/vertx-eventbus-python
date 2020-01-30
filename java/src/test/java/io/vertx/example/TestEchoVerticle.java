package io.vertx.example;

import org.junit.Test;

import io.vertx.core.json.JsonObject;
import io.vertx.example.echo.EchoVerticle;
import io.vertx.example.util.VertxStarter;

/**
 * test the echo verticle
 * @author wf
 *
 */
public class TestEchoVerticle {
  @Test
  public void testEchoVerticle() throws Exception {
    VertxStarter starter=VertxStarter.getStarter(true);
    EchoVerticle echoVerticle = new EchoVerticle();
    starter.start(echoVerticle);
    String msg=starter.waitDeployed(echoVerticle);
    System.out.println(msg);
    JsonObject jo=new JsonObject();
    jo.put("luke","may the force be with you");
    starter.getVertx().eventBus().send("echo",jo);
    Thread.sleep(500);
    starter.close();
  }
}
