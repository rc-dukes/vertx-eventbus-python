package io.vertx.example.util;

import io.vertx.ext.bridge.BridgeOptions;
import io.vertx.ext.bridge.PermittedOptions;
import io.vertx.ext.eventbus.bridge.tcp.TcpEventBusBridge;
import io.vertx.reactivex.core.Vertx;

/**
 * starter for TcpEventBusBridge
 * 
 * @author wf
 *
 */
public class TcpEventBusBridgeStarter {

  private Vertx vertx;
  private String inboundRegex;
  private String outboundRegex;
  private int port;
  private TcpEventBusBridge bridge;
  private boolean allowExit=false;

  /**
   * construct me
   * @param vertx
   * @param inboundRegex
   * @param outboundRegex
   * @param port
   */
  public TcpEventBusBridgeStarter(Vertx vertx, String inboundRegex,String outboundRegex,int port) {
    this.vertx=vertx;
    this.inboundRegex=inboundRegex;
    this.outboundRegex=outboundRegex;
    this.port=port;
  }

  /**
   * start the bridge
   */
  public void start() {
    bridge = TcpEventBusBridge.create(vertx.getDelegate(),
        new BridgeOptions()
            .addInboundPermitted(
                new PermittedOptions().setAddressRegex(inboundRegex))
            .addOutboundPermitted(
                new PermittedOptions().setAddressRegex(outboundRegex)));

    bridge.listen(port, res -> {
      if (res.succeeded()) {

      } else {
        System.err.println("listen failed - can't start TcpEventBusBridge");
        System.err.println(
            "is there another process listening on port " + port + "?");
        if (isAllowExit())
          System.exit(1);
      }
    });
  }

  /**
   * @return the allowExit
   */
  public boolean isAllowExit() {
    return allowExit;
  }

  /**
   * @param allowExit the allowExit to set
   */
  public void setAllowExit(boolean allowExit) {
    this.allowExit = allowExit;
  }
}
