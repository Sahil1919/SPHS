
import re
import pandas as pd
import pytesseract 
import cv2
import glob
import easygui
import time
class AdharInfo_Extractor():
    def __init__(self,front_img:str,back_img:str):
          
        img = cv2.imread(front_img)
        config = '--psm 3'
        self.ocr_text = pytesseract.image_to_string(img, lang='eng', config=config)

        self.adhar_number = self.find_adhar_number(self.ocr_text)
        self.adhar_name = self.find_name(self.ocr_text)
        self.adhar_dob = self.find_dob(self.ocr_text)
        self.adhar_gender = self.find_gender(self.ocr_text)
        self.adhar_address = self.find_address(back_img)

     
    def find_adhar_number(self,ocr_text:str):
            
            adhar_number_patn = '[0-9]{4}\s[0-9]{4}\s[0-9]{4}'
            match = re.search(adhar_number_patn, ocr_text)
            if match:
                return match.group().replace(' ','')
            

    def find_name(self,ocr_text:str):
            
            adhar_name_patn = r'\b[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+$'
            split_ocr = ocr_text.split('\n')
            for ele in split_ocr:
                match = re.search(adhar_name_patn, ele)
                if match:
                    return match.group()
                
    def find_dob(self,ocr_text:str):
            
            dob_patn = '\d+[-/]\d+[-/]\d+'
            yob_patn = '[0-9]{4}'
            DateOfBirth = ''
            if 'DOB' in ocr_text:
                match = re.search(dob_patn, ocr_text)
                DateOfBirth = match.group()
            if 'Year of Birth' in ocr_text:
                match = re.search(yob_patn, ocr_text)
                DateOfBirth = match.group()
            return DateOfBirth

    def find_gender(self,ocr_text:str):
            regex = "Male|Female|MALE|FEMALE"
            gen = re.findall(regex, ocr_text)
            if gen:
                 GENDER = gen[0]
            else:
                 GENDER = 'NAN'
            
            return GENDER

    def find_address(self,backimg):
            
            try:
                img = cv2.imread(backimg)
                h,w = img.shape[:2]
                cropped_image = img[250:-100, 32:int(w/1.6)]
                
                # Display cropped image
                # cv2.imshow("cropped", cropped_image)
                # cv2.waitKey(0)
 #               cv2.destroyAllWindows()
                config = '--psm 3'
                img = cropped_image
                ocr_text = pytesseract.image_to_string(img, lang='eng', config=config).replace('\n', ' ').replace('"', '')
                
                address_start = re.search('Address', ocr_text).end()
                address = ocr_text[address_start:]
                pinpatn = r'[0-9]{6}'
                address_end = 0
                pinloc = re.search(pinpatn, address)
                if pinloc:
                    address_end = pinloc.end()
                    address = address[:address_end]
                else:
                    print('Pin code not found in address')
                    address = re.sub('\n', ' ', address[:address_end])

                address = address.split(':')
                if len(address)>1:
                    chr_remove = '!@#$©'
                    address = ' '.join([x for add in address for x in add.split() if x not in chr_remove])
                                
                return address.strip()
            
            except:
                print("Adhar Back Image Quality is not good ")
                return None

if __name__ == '__main__':

        
    pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

    DF = pd.DataFrame(columns=["Student Name","Adhar Number","DOB","Gender","Address"])
    # DF.index.name = "SR NO"
    # DF.index  = False

    print("Select Folder where Adhar Image is located !")
    time.sleep(2)
    adhar_file_path = easygui.diropenbox()    

    list_front_img = [file for file in glob.glob(f"{adhar_file_path}/*") if ".1." not in file]
    list_back_img = [file for file in glob.glob(f"{adhar_file_path}/*") if ".1." in file]
    
    print("Select Folder where you want to save Excel file !")
    time.sleep(2)
    excel_file_path = easygui.diropenbox()

    for front_img,back_img in zip(list_front_img,list_back_img):
        
        adhar_info_extractor = AdharInfo_Extractor(front_img,back_img)

        adhar_number = adhar_info_extractor.adhar_number
        adhar_name = adhar_info_extractor.adhar_name
        adhar_dob = adhar_info_extractor.adhar_dob
        adhar_gender = adhar_info_extractor.adhar_gender
        adhar_address = adhar_info_extractor.adhar_address

        details = [adhar_name, adhar_number, adhar_dob, adhar_gender, adhar_address]
        DF.loc[len(DF)+1] = details
        
        print(adhar_name)
        print(adhar_number)
        print(adhar_dob)
        print(adhar_gender)
        print(adhar_address)

        print("----------------------------------------------------")

    
    DF.to_excel(excel_file_path+"/StudentDetails.xlsx",index=False)