package io.vertx.example.util;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import io.vertx.core.DeploymentOptions;
import io.vertx.core.Verticle;
import io.vertx.core.Vertx;
import io.vertx.core.VertxOptions;

/**
 * Vert.x starter
 * 
 * @author <a href="http://tfox.org">Tim Fox</a>
 * @author wf
 */
public class VertxStarter {

  private static final String RX_EXAMPLES_DIR = ".";
  private static final String RX_EXAMPLES_JAVA_DIR = RX_EXAMPLES_DIR
      + "/src/main/java/";
  private static final int MAX_DEPLOYMENT_TIME = 20000;
  private VertxOptions options;
  private String exampleDir;
  private DeploymentOptions deploymentOptions;
  private List<Verticle> startedVerticle = new ArrayList<Verticle>();
  private Vertx vertx;

  /**
   * construct me with the given parameters
   * 
   * @param exampleDir
   *          - the example directory
   * @param clustered
   */
  public VertxStarter(String exampleDir, boolean clustered) {
    this.exampleDir = exampleDir;
    this.options = getOptions(clustered);
  }

  /**
   * start me and return me
   * 
   * @return the starter
   */
  public VertxStarter start(Verticle... verticles) {
    setCwd();
    for (Verticle verticle : verticles) {
      startVerticle(verticle);
    }
    return this;
  }

  /**
   * start the verticle with the given Class
   * 
   * @param verticleClass
   */
  public void startVerticle(Verticle verticle) {
    Consumer<Vertx> starter = vertx -> {
      try {
        if (deploymentOptions != null) {
          vertx.deployVerticle(verticle, deploymentOptions);
        } else {
          vertx.deployVerticle(verticle);
        }
        startedVerticle.add(verticle);
      } catch (Throwable t) {
        handle(t);
      }
    };
    if (options.getEventBusOptions().isClustered()) {
      Vertx.clusteredVertx(options, res -> {
        if (res.succeeded()) {
          vertx = res.result();
          starter.accept(vertx);
        } else {
          res.cause().printStackTrace();
        }
      });
    } else {
      vertx = Vertx.vertx(options);
      starter.accept(vertx);
    }
  }
  
  /**
   * close
   */
  public void close() {
    if (vertx!=null)
      vertx.close();
  }

  /**
   * wait for the given verticle to be deployed
   * @param verticle
   * @throws Exception
   */
  public String waitDeployed(Verticle verticle) throws Exception {
    int loopTime = 40; // 25 checks per second
    int timeLeft = MAX_DEPLOYMENT_TIME;
    while (timeLeft > 0) {
      if (this.startedVerticle.contains(verticle)) {
        String msg=String.format("%s deployed after %.1f secs",verticle.getClass().getSimpleName(),(MAX_DEPLOYMENT_TIME-timeLeft)/1000.0);
        return msg;
      }
      Thread.sleep(loopTime);
      timeLeft -= loopTime;
    }
    String msg=String.format("wait Deployed timed out after %.1f secs",MAX_DEPLOYMENT_TIME/1000.0);
    throw new Exception(msg);
  }

  /**
   * error handler
   * 
   * @param t
   *          - the Throwable to handle
   */
  private void handle(Throwable t) {
    t.printStackTrace();
  }

  /**
   * set the current working Directory for vert.x
   * 
   * @return - the directory set
   */
  public String setCwd() {
    // Smart cwd detection

    // Based on the current directory (.) and the desired directory
    // (exampleDir), we try to compute the vertx.cwd
    // directory:
    try {
      // We need to use the canonical file. Without the file name is .
      File current = new File(".").getCanonicalFile();
      if (exampleDir.startsWith(current.getName())
          && !exampleDir.equals(current.getName())) {
        exampleDir = exampleDir.substring(current.getName().length() + 1);
      }
    } catch (IOException e) {
      handle(e);
    }

    System.setProperty("vertx.cwd", exampleDir);
    return exampleDir;
  }

  /**
   * get the vert.x options for the given clustered mode
   * 
   * @param clustered
   * @return the options
   */
  public VertxOptions getOptions(boolean clustered) {
    VertxOptions options = new VertxOptions();
    options.getEventBusOptions().setClustered(clustered);
    return options;
  }

  /**
   * run a clustered Example
   * 
   * @param verticle
   *          - the
   * @return - the starter
   */
  public static VertxStarter runClusteredExample(Verticle verticle) {
    return getStarter(true).start(verticle);
  }

  /**
   * run a non-clustered example
   * 
   * @param clazz
   *          - the
   * @return - the starter
   */
  public static VertxStarter runExample(Verticle verticle) {
    return getStarter(false).start(verticle);
  }

  /**
   * get a default starter with the given clustered mode
   * 
   * @param clustered
   * @return - the starter
   */
  public static VertxStarter getStarter(boolean clustered) {
    VertxStarter starter = new VertxStarter(RX_EXAMPLES_JAVA_DIR, clustered);
    return starter;
  }

}
