from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options


class CalculatePerson():
    def __init__(self, userdata):
        self.height = userdata.height
        self.weight = userdata.weight
        self.age = userdata.age
        self.gender = userdata.gender
        self.stregnth = userdata.stregnth
        self.calories = None

    def calculate_bmi(self):
        BMI = self.weight / ((self.height / 100) ** 2)
        if BMI < 18.5:
            return "過輕"
        elif BMI >= 18.5 and BMI < 24:
            return "適中"
        else:
            return "過重"

    def calculate_calories_daily(self):
        if self.stregnth == "1":

            if self.calculate_bmi() == "過輕":
                self.calories = 35 * self.weight
                return self.calories

            elif self.calculate_bmi() == "適中":
                self.calories = 30 * self.weight
                return self.calories

            else:
                self.calories = 22.5 * self.weight
                return self.calories

        elif self.stregnth == "2":

            if self.calculate_bmi() == "過輕":
                self.calories = 40 * self.weight
                return self.calories

            elif self.calculate_bmi() == "適中":
                self.calories = 35 * self.weight
                return self.calories

            else:
                self.calories = 30 * self.weight
                return self.calories
        else:

            if self.calculate_bmi() == "過輕":
                self.calories = 45 * self.weight
                return self.calories

            elif self.calculate_bmi() == "適中":
                self.calories = 40 * self.weight
                return self.calories

            else:
                self.calories = 35 * self.weight
                return self.calories

    def calculate_calories(self, consumption):

        self.calories = self.calculate_calories_daily()- consumption
        return self.calories

    def exercise_caloris_consumption(self, extra_calories):

        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome("chromedriver.exe", options=options)
        driver.get("https://met.0123456789.tw/")

        height = driver.find_element_by_name("yourh")
        height.send_keys(str(self.height))
        weight = driver.find_element_by_name("yourw")
        weight.send_keys(str(self.weight))
        age = driver.find_element_by_name("youra")
        age.send_keys(str(self.age))
        time_use = driver.find_element_by_name("yourtime")
        time_use.send_keys("1")
        button = driver.find_element_by_css_selector("input[type='button']")
        button.click()
        exercise_dic = {}

        tbody = driver.find_elements_by_tag_name("tbody")[1]
        trs = tbody.find_elements_by_tag_name("tr")

        for i in range(1, len(trs) - 1):
            tds = trs[i].find_elements_by_tag_name("td")
            item = tds[0].text.split("\n")
            man_value = float(tds[1].find_element_by_tag_name("input").get_attribute("value"))
            woman_value = float(tds[2].find_element_by_tag_name("input").get_attribute("value"))
            key = f"item{i}"
            if self.gender == "男":
                man_minute = round(abs(extra_calories / man_value), 2)
                exercise_dic[key] = [item, man_minute]
            elif self.gender == "女":
                woman_minute = round(abs(extra_calories / woman_value), 2)
                exercise_dic[key] = [item, woman_minute]
        return exercise_dic


def calculate_consumption(food_list):
    food_dic = {
        "Bambooshoots": ["竹筍", 28, 2.6],
        "Beansprouts": ["豆芽菜", 34, 4.6],
        "Cabbage": ["高麗菜", 23, 1.3],
        "Driedtofu": ["豆干", 161, 19],
        "Fish": ["魚", 155, 25],
        "Friedchickenlegs": ["炸雞腿", 500, 20],
        "Friedshrimp": ["炸蝦", 224, 11.5],
        "Friedsteak": ["炸排", 383, 29],
        "Fungus": ["木耳", 31, 2],
        "Shiitake": ["香菇", 40, 3.4],
        "Shrimp": ["蝦子", 11, 2.2],
        "Slicedmeat": ["肉片", 250, 20.3],
        "broccoli": ["花椰菜", 28, 3.7],
        "carrot": ["紅蘿蔔", 41, 1.1],
        "cauliflower": ["白花椰", 23, 1.8],
        "chicken": ["雞肉", 109, 24.2],
        "chickenlegs": ["雞腿", 200, 18.5],
        "corn": ["玉米", 108, 4.7],
        "egg": ["蛋", 77, 11],
        "eggplant": ["茄子", 77, 2],
        "green": ["綠色蔬菜", 30, 2],
        "halfegg": ["半顆蛋", 33, 5],
        "omelet": ["炒蛋", 95, 12],
        "pork": ["控肉", 320, 10],
        "pumpkin": ["南瓜", 91, 2],
        "ribs": ["排骨", 240, 19],
        "riceflour": ["米粉", 327, 8.1],
        "sausage": ["香腸", 300, 16],
        "shelledShrimp": ["蝦仁", 10, 2.2],
        "sunegg": ["荷包蛋", 85, 2],
        "tofu": ["豆腐", 90, 6]
    }
    calories_comsupion = 0
    protein_consumptioln = 0
    food_name_set = set()
    food_name = " "

    for food_detection in food_list:
        calories_comsupion = calories_comsupion + food_dic[food_detection][1]

        protein_consumptioln = protein_consumptioln + food_dic[food_detection][2]
        food_name_set.add(food_dic[food_detection][0])

    for name in food_name_set:
        food_name = name + "," + food_name

    return food_name, calories_comsupion, round(protein_consumptioln, 2)




def get_coordinate(addr):
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    browser = webdriver.Chrome(executable_path='chromedriver', options=options)
    browser.get("http://www.map.com.tw/")
    search = browser.find_element_by_id("searchWord")
    search.clear()
    search.send_keys(addr)
    browser.find_element_by_xpath("/html/body/form/div[10]/div[2]/img[2]").click()
    time.sleep(2)
    iframe = browser.find_elements_by_tag_name("iframe")[0]
    browser.switch_to.frame(iframe)
    coor_btn = browser.find_element_by_xpath("/html/body/form/div[4]/table/tbody/tr[3]/td/table/tbody/tr/td[2]")
    coor_btn.click()
    coor = browser.find_element_by_xpath("/html/body/form/div[5]/table/tbody/tr[2]/td")
    coor = coor.text.strip().split(" ")
    lat = coor[-1].split("：")[-1]
    log = coor[0].split("：")[-1]
    browser.quit()
    return (lat, log)


def find_food(lat, lng):
    url = f"https://ifoodie.tw/explore/list?latlng={lat}%2C{lng}&sortby=recent"
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    browser = webdriver.Chrome(executable_path='chromedriver', options=options)
    browser.get(url)
    search_rs = browser.find_elements_by_class_name("restaurant-info")

    res_dict = {}
    for search_r in search_rs:
        title = search_r.find_elements_by_class_name("title")[0]
        address = search_r.find_elements_by_class_name("address-row")[0]
        res_dict[title.text] = address.text
        return res_dict












