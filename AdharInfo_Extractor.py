import re
import pytesseract 
import cv2

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
            if 'Male' in ocr_text or 'MALE' in ocr_text:
                GENDER = 'Male'
            elif 'Female' in ocr_text or 'FEMALE' in ocr_text:
                GENDER = 'Female'
            else:
                GENDER = 'NAN'
            return GENDER

    def find_address(self,backimg):
            
            img = cv2.imread(backimg)
            h,w = img.shape[:2]
            cropped_image = img[250:-100, 32:int(w/1.6)]
            
            # Display cropped image
            cv2.imshow("cropped", cropped_image)
            cv2.waitKey(0)

            config = '--psm 3'
            img = cropped_image
            ocr_text = pytesseract.image_to_string(img, lang='eng', config=config).replace('\n', ' ').replace('"', '')
            # print(ocr_text) # Print)

            # address_start = ocr_text.find('Address')
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

if __name__ == '__main__':

        
    # pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

    front_img = "D:/Docx_converter/A3.jpeg"
    back_img = "D:/Docx_converter/A1.1.jpeg"

    adhar_info_extractor = AdharInfo_Extractor(front_img,back_img)
    
    print(adhar_info_extractor.adhar_number)
    print(adhar_info_extractor.adhar_name)
    print(adhar_info_extractor.adhar_dob)
    print(adhar_info_extractor.adhar_gender)
    print(adhar_info_extractor.adhar_address)

    