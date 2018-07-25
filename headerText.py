def FunctionStarts ():
  #input number in reformatter_[number] and the imports
  #make sure number is Letter-3 digits-Letter
  #I just realized... you'd have to make the ECL file and name it before you even start, so asking for the number is moot. 
  #reformatterNum = raw_input("Input the number of the reformatter e.g. S054A")
  outfile = open("output.txt", "a+")
  #outfile.write("EXPORT reformatter_{}(string fname) := FUNCTION\n".format(reformatterNum))
  outfile.write("import HC_Data_Sharecare_Shared, STD;\n")
  outfile.write("\n")
  outfile.write("c := HC_Data_Sharecare_Shared.Constants;\n")
  outfile.write("f := HC_Data_Sharecare_Shared.Functions;\n")
  outfile.write("\n")
  outfile.close()

def HeaderPart(client_fields, isFixedLength):
  #asking for layout name
  layoutName = raw_input("What's the name of the client? (This is for use for the layout name, nothing more)")

  outfile = open("output.txt", "a+")
  outfile.write("layout_{} := RECORD\n".format(layoutName))
  for cField in client_fields:
    positionOfDash = cField.find("-")
    if(positionOfDash != -1):
      stringSize = cField[positionOfDash+1:]
      theString = cField[:positionOfDash]
      outfile.write("STRING{} {};\n".format(stringSize, theString))
    else:
      outfile.write("string {};\n".format(cField))
  outfile.write("END;\n")
  outfile.write("\n")
  outfile.close()

  #boilerplate for utlizing filenames
  outfile = open("output.txt", "a+")
  outfile.write("myName := HC_Data_Sharecare_Shared.FileNames.getFromFileName(fname);\n")
  outfile.write("SprayName := HC_Data_Sharecare_Shared.FileNames.sprayname(myName.datamodel, myName.OrbitCustomerId, (string) myName.ReceivingInstanceId);\n")
  outfile.write("ReformatName := HC_Data_Sharecare_Shared.FileNames.reformatname(myName.datamodel, myName.OrbitCustomerId, (string) myName.ReceivingInstanceId);\n")
  outfile.write("\n")
  outfile.close()

  if(isFixedLength.upper() == "N"):
    #now we reach really the next 5%. The header and trailer (footer) bit. 
      #inputDS... I'm not too certain of all the possibilities here. Need to ask Richard.
      #so far I think I need to ask the user if it's a seperated or terminated file,
      #then ask if there's a trim needed (i.e. if there's a header?), if there is, how much (1 seems to be most common)
    #input loop for invalid input on seperated vs terminated
    while True:
      isSeparateorTerminateRaw = raw_input("Is the client file separated or terminated? (Input separated or terminated)")
      if(isSeparateorTerminateRaw.upper() == "SEPARATED"):
        recordBreak = "separator"
        break
      #this will need to be tweaked eventually for fix length files
      if(isSeparateorTerminateRaw.upper() == "TERMINATED"):
        recordBreak = "terminator"
        break

    breakCharacter = raw_input("Input character that delimits the records in the client data (e.g. | or an End of Line)")

    #input loop for invalid input on Y/N for trimming header
    #while True:
      #needTrim = raw_input("Does the client file need to trim a header? Y/N")
      #if(needTrim.upper() == "Y"):
    trimString = "heading"
    headerTrimNum = raw_input("How many header rows need to be trimmed? (Input a NUMBER e.g. 1)")
    headerTrimNumPass = "({})".format(headerTrimNum)
        #break
      #bring this back with fixed legnth files
      #if(needTrim.upper() == "N"):
      # trimString = "NOTRIM"
      # headerTrimNumPass = ""
      # break

  outfile = open("output.txt", "a+")
  #if it's a fixed file, there's no separator... normally. Anything outside the norm the dev's gotta do it. Whomp. 
  if(isFixedLength.upper() == "Y"):
    outfile.write("inputDS := dataset(SprayName, {}, THOR);\n".format("layout_"+layoutName))
  else:
    outfile.write("inputDS := dataset(SprayName, {}, CSV({},{}));\n".format("layout_"+layoutName, recordBreak+"(\'"+breakCharacter+"\')",trimString+headerTrimNumPass))
  outfile.close()