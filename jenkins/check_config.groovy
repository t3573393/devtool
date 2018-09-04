import javax.xml.parsers.DocumentBuilderFactory
import javax.xml.xpath.*

class IniParser {
  def src = null;
  def sections = new ArrayList<String>();
  def config = [:]
  String section = ""
  boolean inSection = false;
  def match = null;
  IniParser(filename) {
    src = new File(filename)
    src.eachLine { line ->
      line.find(/\[(.*)\]/) {full, sec ->
        sections.add(sec)
        inSection = true;
        section = sec
        config[section] = [:]
      }
      line.find(/\s*(\S+)\s*=\s*(.*)?(?:#|$)/) {full, key, value ->
        if (config.get(section).containsKey(key)) {
          def v = config.get(section).get(key)
          if (v in Collection) {
            def oldVal = config.get(section).get(key)
            oldVal.add(value)
            config[key] = oldVal
            config.get(section).put(key, oldVal)
          } else {
            def values = new ArrayList<String>();
            values.add(v)
            values.add(value)
            config.get(section).put(key, values)
          }
        } else {
          config.get(section).put(key, value)
        }
        // println "Match: $full, Key: $key, Value: $value"
        // config.get(section).put(key, value)
      }
    }
  }

  def dumpConfig() {
    config.each() {key, value ->
      println "$key: $value"
    }
  }

  ArrayList<String> getAllSections() {
    return sections
  }

  def getSection(s) {
    return config.get(s)
  }

  def getAllConfig() {
    return config
  }

  def getConfigBySection(String section) {
    return config.get(section)
  }

  def getConfigBySectionAndKey(String section, String key) {
    return config.get(section).get(key)
  }
}

class GroovyCheckTools {
   public static boolean checkXmlValue(String xmlFilePath, String xpathQuery, String value, String fileEncoding='utf-8') {
      String fileContents = new File(xmlFilePath).getText(fileEncoding)
      def xpath = XPathFactory.newInstance().newXPath()
      def builder = DocumentBuilderFactory.newInstance().newDocumentBuilder()
      def inputStream = new ByteArrayInputStream(fileContents.bytes)
      def records = builder.parse(inputStream).documentElement
      String targetValue = xpath.evaluate(xpathQuery, records)
      return value.equals(targetValue)
   }

   public static boolean checkPropertiesValue(String propertiesFilePath, String name, String value) {
      Properties properties = new Properties()
      File propertiesFile = new File(propertiesFilePath)
      propertiesFile.withInputStream{ properties.load(it) }
      def targetValue = properties.getProperty(name)
      return value.equals(targetValue)
   }

   public static boolean checkInivalue(String iniFilePath, String sectionName, String name, String value) {
      def ini = new IniParser(iniFilePath)
	  ini.dumpConfig()
	  def targetValue = ini.getConfigBySectionAndKey(sectionName, name)
      return value.equals(targetValue)
   }
}

def workspacePath = build.project.workspace.toString()

def fileTypeStr = '', filePathStr ='', keyStr= '', valueStr = '', sectionStr = '';
boolean hasVar = false
for (int i=0; i<100; i++) {
   hasVar = false

   if(binding.hasVariable('fileType'+i)) {
      fileTypeStr = binding.getVariable('fileType'+i)
      hasVar = true
   }
   
   if(binding.hasVariable('filePath'+i)) {
      filePathStr = binding.getVariable('filePath'+i)
      hasVar = true
   }
   
   if(binding.hasVariable('key'+i)) {
      keyStr = binding.getVariable('key'+i)
      hasVar = true
   }
   
   if(binding.hasVariable('value'+i)) {
      valueStr = binding.getVariable('value'+i)
      hasVar = true
   }
   
   if(binding.hasVariable('section'+i)) {
      sectionStr = binding.getVariable('section'+i)
      hasVar = true
   }
   
   if (!hasVar) {
      continue
   }  
   
   boolean result = false;
   if (fileTypeStr == 'xml') {
      result=GroovyCheckTools.checkXmlValue("${workspacePath}/${filePathStr}", "${keyStr}", "${valueStr}")
   } else if (fileTypeStr == 'properties') {
      result=GroovyCheckTools.checkPropertiesValue("${workspacePath}/${filePathStr}", "${keyStr}", "${valueStr}")
   } else if (fileTypeStr == 'ini') {
      result=GroovyCheckTools.checkInivalue("${workspacePath}/${filePathStr}",  "${sectionStr}", "${keyStr}", "${valueStr}")
   }
   
   if (!result) {
      throw new RuntimeException("check config error: fileType = ${fileTypeStr}, file = ${workspacePath}/${filePathStr}, key = ${keyStr}, value= ${valueStr}")
   } else {
      println("check config ok: fileType = ${fileTypeStr}, file = ${workspacePath}/${filePathStr}, key = ${keyStr}, value= ${valueStr}, section=${sectionStr}");
   }
}