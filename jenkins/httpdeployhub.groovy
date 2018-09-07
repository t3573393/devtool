import groovy.json.JsonOutput;

// vars/deployhub.groovy
class Deployhub {
    String body="";
    String message="";
    String cookie="";
    String url="";
    String userid="";
    String pw="";
    String postFormStr = "";
    Integer statusCode;
    boolean failure = false;

  def Deployhub(String url) {
    this.url = url;
  }


    def String msg() {
     return "Loading dhactions";
    }

    def parseResponse(HttpURLConnection connection){
        this.statusCode = connection.responseCode;
        this.message = connection.responseMessage;
        this.failure = false;

        if(statusCode == 200 || statusCode == 201){
            this.body = connection.content.text;//this would fail the pipeline if there was a 400
        }else{
            this.failure = true;
            this.body = connection.getErrorStream().text;
        }
        println("body:" + this.body);

        if (cookie.length() == 0)
        {
         String headerName=null;

         for (int i=1; (headerName = connection.getHeaderFieldKey(i))!=null; i++) {
          if (headerName.equals("Set-Cookie")) {
            String c = connection.getHeaderField(i);
            cookie += c + "; ";
          }
         }
		  println("cookie:" + cookie);
        }
    }

    def doGetHttpRequest(String requestUrl){
        URL url = new URL(requestUrl);
        HttpURLConnection connection = url.openConnection();

        connection.setRequestMethod("GET");
        connection.setRequestProperty("Cookie", cookie);
        connection.doOutput = true;

        //get the request
        connection.connect();

        //parse the response
        parseResponse(connection);

        if(failure){
            error("\nGET from URL: $requestUrl\n  HTTP Status: $resp.statusCode\n  Message: $resp.message\n  Response Body: $resp.body");
        }

        this.printDebug("Request (GET):\n  URL: $requestUrl");
        this.printDebug("Response:\n  HTTP Status: $resp.statusCode\n  Message: $resp.message\n  Response Body: $resp.body");
    }

    def Object doGetHttpRequestWithForm(String requestUrl){
        return doHttpRequestWithForm("", requestUrl, "GET");
    }

    def Object doPostHttpRequestWithForm(String formStr, String requestUrl){
        return doHttpRequestWithForm(formStr, requestUrl, "POST");
    }

    def Object doPutHttpRequestWithForm(String formStr, String requestUrl){
        return doHttpRequestWithForm(formStr, requestUrl, "PUT");
    }

    def Object doHttpRequestWithForm(String formStr, String requestUrl, String verb){

        postFormStr = formStr;

        URL url = new URL(requestUrl);
        HttpURLConnection connection = url.openConnection();

        connection.setRequestMethod(verb);
        connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded");
        if (cookie.length() > 0)
          connection.setRequestProperty("Cookie", cookie);
        connection.doOutput = true;

        if (formStr.length() > 0)
        {
         //write the payload to the body of the request
         def writer = new OutputStreamWriter(connection.outputStream);
         writer.write(formStr);
         writer.flush();
         writer.close();
        }

        //post the request
        connection.connect();

        //parse the response
        parseResponse(connection);

        if(failure){
            error("\n$verb to URL: $requestUrl\n    FormStr: $formStr\n    HTTP Status: $statusCode\n    Message: $message\n    Response Body: $body");
            return null;
        }

        return body;

  //      println("Request ($verb):\n  URL: $requestUrl\n  JSON: $json");
  //      println("Response:\n  HTTP Status: $statusCode\n  Message: $message\n  Response Body: $body");
    }

    def String enc(String p)
    {
      return java.net.URLEncoder.encode(p, "UTF-8");
    }

	def login(String userid, String pw)
    {
     this.userid = userid;
     this.pw = pw;

     def res = doPostHttpRequestWithForm("UserId=" + enc(userid) + "&Password=" + enc(pw)+"&Submit="+ enc("提交"), "${url}/console/login.do");

     return res;
    }

	def changeServer(String serverId)
    {
     def res = doPostHttpRequestWithForm("ServerId=" + enc(serverId) + "&_viewReferer=" + enc("server/ChangeCurrentServer"), "${url}/console/ChangeCurrentServer.do");
     return res;
    }

    def bundleList()
    {
     def res = doGetHttpRequestWithForm("${url}/console/BundleList.do");
     return res;
    }

  def listServerPatch(String serverId, String patchId)
  {
     def res = doPostHttpRequestWithForm("PatchId="+enc(patchId)+"&ServerId=" + enc(serverId) + "&_viewReferer=" + enc("bundlex/BundleXAutoPatchPre"), "${url}/console/BundleXAutoPatchPre.do");
     return res
  }

  def bundleAutoStart(String serverIds, String patchId, def bundleLists) {
	def bundleJarsList = [];
	bundleLists.each{it -> bundleJarsList.add("BundleJars="+enc(it.@value.text()))};
	def bundleJarsStr = bundleJarsList.join('&');
	def res = doPostHttpRequestWithForm("PatchId="+enc(patchId)+"&ServerIds=" + enc(serverIds) + "&_viewReferer=" + enc("bundlex/BundleXAutoPatchPre") +"&" + bundleJarsStr, "${url}/console/BundleXAutoPatch.do?Auto-Start=true");
     return res
  }
}

// example for login and do the web deploy
def dh = new Deployhub("<your web site addr>");
def data = dh.login("<your admin username >","<your admin password>");
println("firt login");
//JsonOutput.prettyPrint(JsonOutput.toJson(dh));
def data2 = dh.changeServer("${servers}");
println("change server");
//JsonOutput.prettyPrint(JsonOutput.toJson(dh));

println("bundle list");
dh.bundleList();
//JsonOutput.prettyPrint(JsonOutput.toJson(dh));
println("patch list");
dh.listServerPatch("${servers}", "${patchId}");
//JsonOutput.prettyPrint(JsonOutput.toJson(dh));

// use the xml parser to archive the xml content
@GrabResolver(name="<your maven config name>", root="<your maven repo url >")
@Grab(group='org.ccil.cowan.tagsoup', module='tagsoup', version='1.2')
def tagsoupParser = new org.ccil.cowan.tagsoup.Parser();
def slurper = new XmlSlurper(tagsoupParser);
def htmlParser = slurper.parseText(dh.body);
def bundleJarsList = htmlParser.'**'.findAll{it.@id == 'BundleJars'};
println("bundle start:${servers}");
dh.bundleAutoStart("${servers}", "${patchId}", bundleJarsList);
JsonOutput.prettyPrint(JsonOutput.toJson(dh));
