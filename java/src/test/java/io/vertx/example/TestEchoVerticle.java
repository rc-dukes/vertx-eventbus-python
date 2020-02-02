package io.vertx.example;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import io.vertx.core.eventbus.EventBus;
import io.vertx.core.json.JsonObject;
import io.vertx.example.echo.EchoVerticle;
import io.vertx.example.echo.EchoVerticle.EchoCommand;
import io.vertx.example.util.VertxStarter;

/**
 * test the echo verticle
 * @author wf
 *
 */
public class TestEchoVerticle {
  private static EventBus eb;
  private static VertxStarter starter;
  private static EchoVerticle echoVerticle;
  @BeforeClass
  public static void startEchoVerticle() throws Exception {
    // get a vertX starter
    starter=VertxStarter.getStarter(true);
    // construct an echo Verticle
    echoVerticle = new EchoVerticle();
    // deploy and start it
    starter.start(echoVerticle);
    // wait for the deploy to be successful
    String msg=starter.waitDeployed(echoVerticle);
    System.out.println(msg);
    // get the eventbus
    eb = starter.getVertx().eventBus();
  }
  
  @AfterClass
  public static void tearDown() {
    starter.close();
  }
  
  public void check(Object o, String key,String value) {
    assertNotNull(o);
    assertTrue(o instanceof JsonObject);
    JsonObject rjo=(JsonObject)o;
    assertTrue(rjo.containsKey(key));
    assertEquals(value,rjo.getString(key));
  }
  
  @Test
  public void testPublish() throws Exception {
    // create a JsonObject to send
    JsonObject jo=new JsonObject();
    jo.put("luke","may the force be with you");
    // prepare an array to hold the object received
    Object[] ro= {null};
    // listen to any message for the address echo
    eb.consumer("echo", rmsg->{
      ro[0]=rmsg.body();
    });
    // publish the json object so that we listen to our own message
    eb.publish("echo",jo);
    // wait a bit
    Thread.sleep(500);
    // check that the received object is there
    // and as expected
    check(ro[0],"luke","may the force be with you");
  }
  
  @Test
  public void testCmd() {
    EchoCommand cmd=new EchoCommand("time","send","me");
    String json="{\"cmd\":\"time\",\"msgType\":\"send\",\"address\":\"me\"}";
    String cmdJson=cmd.asJsonObject().toString();
    System.out.println(cmdJson);
    assertEquals(json,cmdJson);
  }   
  
  @Test 
  public void testSendCmd() throws InterruptedException {
    EchoCommand cmd=new EchoCommand("time","send","me");
    
    Object[] ro= {null};
    // listen to any message for the address me
    eb.consumer("me", rmsg->{
      ro[0]=rmsg.body();
    });
    eb.send("echo", cmd.asJsonObject());
    Thread.sleep(500);
    Object o=ro[0];
    assertNotNull(o);
    assertTrue(o instanceof JsonObject);
    JsonObject jo=(JsonObject)o;
    assertTrue(jo.containsKey("received_nanotime"));
    assertTrue(jo.containsKey("iso_time"));
  }
  
}
