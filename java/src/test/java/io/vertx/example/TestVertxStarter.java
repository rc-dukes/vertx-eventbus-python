package io.vertx.example;

import static org.junit.Assert.assertTrue;

import java.io.File;
import java.nio.file.Paths;

import org.junit.Test;

import io.vertx.example.echo.EchoVerticle;
import io.vertx.example.reactivex.eventbus.pubsub.Sender;
import io.vertx.example.util.VertxStarter;

/**
 * test the VertxStarter class
 * @author wf
 *
 */
public class TestVertxStarter {

  @Test
  public void testCwd() {
    VertxStarter starter=VertxStarter.getStarter(true);
    String currentDir=Paths.get(".").toAbsolutePath().normalize().toString();
    String cwdPath=starter.setCwd();
    System.out.println("current directory is "+currentDir);
    System.out.println("cwd is set to "+cwdPath);
    File cwd=new File(cwdPath);
    assertTrue(cwd.exists());
  }
  
  @Test
  public void testEchoVerticle() throws Exception {
    VertxStarter starter=VertxStarter.getStarter(true);
    EchoVerticle echoVerticle = new EchoVerticle();
    starter.start(echoVerticle);
    String msg=starter.waitDeployed(echoVerticle);
    System.out.println(msg);
    starter.close();
  }
  
  @Test
  public void testTwoVerticles() throws Exception {
    VertxStarter starter=VertxStarter.getStarter(true);
    EchoVerticle echoVerticle = new EchoVerticle();
    Sender sendVerticle=new Sender();
    starter.start(echoVerticle,sendVerticle);
    String msg=starter.waitDeployed(sendVerticle);
    System.out.println(msg);
    starter.close();
  }
}
