package io.vertx.example.echo;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.Option;

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

  boolean allowExit;
  public int counter = 0;
  private CmdLineParser parser;

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
    TcpEventBusBridgeStarter bridgeStarter = new TcpEventBusBridgeStarter(vertx,
        inboundRegex, outboundRegex, port);
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
          jo.put("counter", ++counter);
          break;
        case "reset":
          counter = 0;
          jo.put("counter", counter);
          break;
        }
        switch (cmd.msgType) {
        case "send":
          eb.send(cmd.getAddress(), jo);
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
    String msg=String.format("EchoVerticle started on port %d with inboundRegEx %s and outboundRegex %s",this.port,this.inboundRegex,this.outboundRegex);
    System.err.println(msg);
  }

  /**
   * parse the given Arguments
   * 
   * @param args
   * @throws CmdLineException
   */
  public void parseArguments(String[] args) throws CmdLineException {
    parser = new CmdLineParser(this);
    parser.parseArgument(args);
  }

  @Option(name = "-i", aliases = {
      "--inbound" }, usage = "inbound permission regex to be used")
  protected String inboundRegex = "echo.*";
  @Option(name = "-o", aliases = {
      "--outbound" }, usage = "outbound permission regex to be used")
  protected String outboundRegex = "echo.*";
  @Option(name = "-p", aliases = {
      "--port" }, usage = "port to listen for eventbus messages")
  public int port = 7001;
  @Option(name = "-d", aliases = {
  "--debug" }, usage = "show debug output")
  public boolean debug=false;
  
  @Option(name = "-h", aliases = {
  "--help" }, usage = "show this usage")
  public boolean showHelp=false;
  
  /**
   * main rerouted from static to instance call
   * 
   * @param args
   */
  private void mainInstance(String[] args) {
    try {
      parseArguments(args);
      if (showHelp) {
        parser.printUsage(System.out);
        System.exit(0);
      }

    } catch (CmdLineException cle) {
      parser.printUsage(System.err);
      System.exit(1);
    }
    VertxStarter.runClusteredExample(this);
  }

  // Convenience method so you can run it in your IDE
  public static void main(String[] args) {
    EchoVerticle echoVerticle = new EchoVerticle(true);
    echoVerticle.mainInstance(args);
  }

}
