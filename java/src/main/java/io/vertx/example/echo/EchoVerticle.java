package io.vertx.example.echo;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import io.vertx.core.Promise;
import io.vertx.core.json.JsonObject;
import io.vertx.example.util.TcpEventBusBridgeStarter;
import io.vertx.example.util.VertxStarter;
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
  public int counter=0;

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

  public static class EchoCommand {
    String cmd;
    String msgType;
    String address;

    public String getCmd() {
      return cmd;
    }

    public void setCmd(String cmd) {
      this.cmd = cmd;
    }

    public String getMsgType() {
      return msgType;
    }

    public void setMsgType(String msgType) {
      this.msgType = msgType;
    }

    public String getAddress() {
      return address;
    }

    public void setAddress(String address) {
      this.address = address;
    }
    
    // default constructor to allow to map from json
    public EchoCommand() {
      
    }

    /**
     * construct me
     * 
     * @param cmd
     * @param msgType
     * @param address
     */
    public EchoCommand(String cmd, String msgType, String address) {
      this.cmd = cmd;
      this.msgType = msgType;
      this.address = address;
    }

    /**
     * get a cmd from the given json string
     * 
     * @param json
     * @return - the command
     */
    public static EchoCommand fromJson(String json) {
      JsonObject jo = new JsonObject(json);
      EchoCommand cmd = jo.mapTo(EchoCommand.class);
      return cmd;
    }

    public JsonObject asJsonObject() {
      return JsonObject.mapFrom(this);
    }
  }

  @Override
  public void start(Promise<Void> promise) {
    TcpEventBusBridgeStarter bridgeStarter=new TcpEventBusBridgeStarter(vertx,"echo.*","echo.*",port);
    bridgeStarter.setAllowExit(allowExit);
    bridgeStarter.start();
    EventBus eb = vertx.eventBus();

    MessageConsumer<JsonObject> consumer = eb.consumer("echo", message -> {
      JsonObject jo = message.body();
      String headerText = getHeaderText(message.headers(), "  ");
      long time = System.nanoTime();

      String msg = String.format(
          "Echo Verticle received:\n%s\nheaders:\n%s\n will reply it back now with received_time timestamp %d...",
          jo, headerText, time);
      System.out.println(msg);
      // is the received json object a command?
      if (jo.containsKey("cmd")) {
        EchoCommand cmd = jo.mapTo(EchoCommand.class);
        switch (cmd.getCmd()) {
        case "time":
          jo.put("received_nanotime", time);
          SimpleDateFormat sdf = new SimpleDateFormat(
              "yyyy-MM-dd HH:mm:ss.SSS");
          Date now = new Date();
          jo.put("iso_time", sdf.format(now));
          break;
        case "counter":
          jo.put("counter",++counter);
          break;
        case "reset":
          counter=0;
          jo.put("counter", counter);
          break;
        }
        switch (cmd.msgType) {
        case "send":
          eb.send(cmd.getAddress(),jo);
          break;
        case "publish":
          eb.publish(cmd.getAddress(), jo);
          break;
        }
      }
      message.reply(jo);
      System.out.println(jo);
    });
    promise.complete();
  }

  // Convenience method so you can run it in your IDE
  public static void main(String[] args) {
    VertxStarter.runClusteredExample(new EchoVerticle(true));
  }
}
