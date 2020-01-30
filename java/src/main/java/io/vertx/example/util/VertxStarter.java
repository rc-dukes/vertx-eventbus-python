package io.vertx.example.util;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

import io.vertx.core.AbstractVerticle;
import io.vertx.core.DeploymentOptions;
import io.vertx.core.Verticle;
import io.vertx.core.Vertx;
import io.vertx.core.VertxOptions;
import io.vertx.core.AsyncResult;
import io.vertx.core.Handler;

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
  private Map<String, AbstractVerticle> startedVerticles = new HashMap<String, AbstractVerticle>();
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
    Handler<AsyncResult<String>> completionHandler = x -> {
      if (x.succeeded()) {
        if (verticle instanceof AbstractVerticle) {
          AbstractVerticle averticle = (AbstractVerticle) verticle;
          startedVerticles.put(averticle.deploymentID(), averticle);
        }
      }
    };
    Consumer<Vertx> starter = vertx -> {
      try {
        if (deploymentOptions != null) {
          vertx.deployVerticle(verticle, deploymentOptions, completionHandler);
        } else {
          vertx.deployVerticle(verticle, completionHandler);
        }
      } catch (Throwable t) {
        handle(t);
      }
    };
    if (options.getEventBusOptions().isClustered()) {
      Vertx.clusteredVertx(options, res -> {
        if (res.succeeded()) {
          setVertx(res.result());
          starter.accept(getVertx());
        } else {
          res.cause().printStackTrace();
        }
      });
    } else {
      setVertx(Vertx.vertx(options));
      starter.accept(getVertx());
    }
  }

  /**
   * undeploy the given abstract verticle
   * 
   * @param averticle
   */
  public void undeploy(AbstractVerticle averticle) {
    getVertx().undeploy(averticle.deploymentID());
    this.startedVerticles.remove(averticle.deploymentID());
  }

  /**
   * close
   */
  public void close() {
    if (getVertx() != null) {
      getVertx().close();
    }
  }

  /**
   * wait for the given verticle to be deployed
   * 
   * @param verticle
   * @throws Exception
   */
  public String waitDeployed(Verticle verticle) throws Exception {
    int loopTime = 40; // 25 checks per second
    int timeLeft = MAX_DEPLOYMENT_TIME;
    while (timeLeft > 0) {
      if (this.startedVerticles.containsValue(verticle)) {
        String msg = String.format("%s deployed after %.1f secs",
            verticle.getClass().getSimpleName(),
            (MAX_DEPLOYMENT_TIME - timeLeft) / 1000.0);
        return msg;
      }
      Thread.sleep(loopTime);
      timeLeft -= loopTime;
    }
    String msg = String.format("wait Deployed timed out after %.1f secs",
        MAX_DEPLOYMENT_TIME / 1000.0);
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

  /**
   * @return the vertx
   */
  public Vertx getVertx() {
    return vertx;
  }

  /**
   * @param vertx
   *          the vertx to set
   */
  public void setVertx(Vertx vertx) {
    this.vertx = vertx;
  }

}
