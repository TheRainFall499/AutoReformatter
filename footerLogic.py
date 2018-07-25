def MakeFooterLogic () :
  while True:
    footerRecordFields = raw_input("List the fieldnames for the footer in a space delimited list e.g. A B C with the Record_Count field named exactly as \"Record_Count\"\n")
    if("Record_Count" in footerRecordFields):
      footerRecordArray = footerRecordFields.split(" ")
      break
    else:
      print("We kinda care about having a Record_Count field. Try again.")

  outfile = open("output.txt", "a+")
  outfile.write("footer_record := RECORD\n")
  #writing out footer_record
  for field in footerRecordArray:
    outfile.write("string "+field+";\n")
  outfile.write("END;\n")
    #the getting of record numbers and what not is... easy, hard code strings.
  outfile.write("unsigned fileCount := COUNT(inputDS);\n")
  outfile.write("footerRow := inputDS[fileCount];\n")
  outfile.write("unsigned numberofrows := IF( fileCount>0,fileCount-1,1 );\n")
  outfile.write("inputNoFooter := inputDS[1..numberofrows];\n")
    #the inputFooter transformation will be odd as apparently not everything lines up with the first rows of the layout?
    #turns out the only part that's consistenly used, i.e. the only part I care about, is which field corresponds to record count
  recordCountField = raw_input("What field of the client file corresponds to the footer record count?")
  outfile.write("inputFooter := project(inputDS[fileCount], transform(footer_record, self.Record_Count := left.{}; ));\n".format(recordCountField))
    #then from there the rest of the stuff is also hard code strings
  outfile.write("footermsg := 'Number of Records Validation Failed.  Footer indicates ' + inputFooter.Record_Count + ' records, but file contains ' + numberofrows + ' records.';\n")
  outfile.write("BOOLEAN GoodFooterValidation := numberofrows = (unsigned) inputFooter.Record_Count;\n")
  outfile.write("footerOut := output( footerRow, named('FooterRecord') );\n")
  outfile.write("footerAssert := sequential(IF( not GoodFooterValidation, HC_Data_Sharecare_Shared.Actions.reformatFailed(fname, footermsg)), ASSERT( GoodFooterValidation, footermsg, FAIL ));\n")
  outfile.write("\n")
  outfile.close()