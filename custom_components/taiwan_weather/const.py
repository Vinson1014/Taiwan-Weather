"""Constants for Taiwan Weather Integration."""
from homeassistant.components.weather import (
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,
)
from homeassistant.const import Platform

DOMAIN = "taiwan_weather"  # 此集成在 Home Assistant 中的唯一識別符
ATTRIBUTION = "Provided by CWA OpenData"  # 屬性值，用於顯示資料來源
MANUFACTURER = "CWA Open Weather Data"  # 製造商名稱


# Platform 相關常數
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.WEATHER]

# 預設值和更新週期
DEFAULT_NAME = "Taiwan Weather"
UPDATE_INTERVAL = 60  # 分鐘


# API 相關資訊
API_BASE_URL  = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"

API_LOCATION_MAPPING = {
    "鄉鎮天氣預報": {
        "id": "F-D0047",
        "forecast_duration_type": {
            "three_days" : "三日預報",
            "weekly" : "一周預報"
        },
        "location": {
            "宜蘭縣": {
                "three_days": "001", # F-D0047-001
                "weekly": "003", # F-D0047-003
                "district": ["頭城鎮", "礁溪鄉", "壯圍鄉", "員山鄉", "宜蘭市", "大同鄉", "五結鄉", "三星鄉", "羅東鎮", "冬山鄉", "南澳鄉", "蘇澳鎮"]
            },
            "桃園市": {
                "three_days": "005", # F-D0047-005
                "weekly": "007", # F-D0047-007
                "district": ["大園區", "蘆竹區", "觀音區", "龜山區", "桃園區", "中壢區", "新屋區", "八德區", "平鎮區", "楊梅區", "大溪區", "龍潭區", "復興區"]
            },
            "新竹縣": {
                "three_days": "009", # F-D0047-009
                "weekly": "011", # F-D0047-011
                "district": ["新豐鄉", "湖口鄉", "新埔鎮", "竹北市", "關西鎮", "芎林鄉", "竹東鎮", "寶山鄉", "尖石鄉", "橫山鄉", "北埔鄉", "峨眉鄉", "五峰鄉"]
            },
            "苗栗縣": {
                "three_days": "013", # F-D0047-013
                "weekly": "015", # F-D0047-015
                "district": ["竹南鎮", "頭份市", "三灣鄉", "造橋鄉", "後龍鎮", "南庄鄉", "頭屋鄉", "獅潭鄉", "苗栗市", "西湖鄉", "通霄鎮", "公館鄉", "銅鑼鄉", "泰安鄉", "苑裡鎮", "大湖鄉", "三義鄉", "卓蘭鎮"]
            },
            "彰化縣": {
                "three_days": "017", # F-D0047-017
                "weekly": "019", # F-D0047-019
                "district": ["伸港鄉", "和美鎮", "線西鄉", "鹿港鎮", "彰化市", "秀水鄉", "福興鄉", "花壇鄉", "芬園鄉", "芳苑鄉", "埔鹽鄉", "大村鄉", "二林鎮", "員林市", "溪湖鎮", "埔心鄉", "永靖鄉", "社頭鄉", "埤頭鄉", "田尾鄉", "大城鄉", "田中鎮", "北斗鎮", "竹塘鄉", "溪州鄉", "二水鄉"]
            },
            "南投縣": {
                "three_days": "021", # F-D0047-021
                "weekly": "023", # F-D0047-023
                "district": ["仁愛鄉", "國姓鄉", "埔里鎮", "草屯鎮", "中寮鄉", "南投市", "魚池鄉", "水里鄉", "名間鄉", "信義鄉", "集集鎮", "竹山鎮", "鹿谷鄉"]
            },
            "雲林縣": {
                "three_days": "025", # F-D0047-025
                "weekly": "027", # F-D0047-027
                "district": ["麥寮鄉", "二崙鄉", "崙背鄉", "西螺鎮", "莿桐鄉", "林內鄉", "臺西鄉", "土庫鎮", "虎尾鎮", "褒忠鄉", "東勢鄉", "斗南鎮", "四湖鄉", "古坑鄉", "元長鄉", "大埤鄉", "口湖鄉", "北港鎮", "水林鄉", "斗六市"]
            },
            "嘉義縣": {
                "three_days": "029", # F-D0047-029
                "weekly": "031", # F-D0047-031
                "district": ["大林鎮", "溪口鄉", "阿里山鄉", "梅山鄉", "新港鄉", "民雄鄉", "六腳鄉", "竹崎", "鄉", "東石鄉", "太保市", "番路鄉", "朴子市", "水上鄉", "中埔鄉", "布袋鎮", "鹿草鄉", "義竹鄉", "大埔鄉"]
            },
            "屏東縣": {
                "three_days": "033", # F-D0047-033
                "weekly": "035", # F-D0047-035
                "district": ["高樹鄉", "三地門鄉", "霧臺鄉", "里港鄉", "鹽埔鄉", "九如鄉", "長治鄉", "瑪家鄉", "屏東市", "內埔鄉", "麟洛鄉", "泰武鄉", "萬巒鄉", "竹田鄉", "萬丹鄉", "來義鄉", "潮州鎮", "新園鄉", "崁頂鄉", "新埤鄉", "南州鄉", "東港鎮", "林邊鄉", "佳冬鄉", "春日鄉", "獅子鄉", "琉球鄉", "枋山鄉", "牡丹鄉", "滿州鄉", "車城鄉", "恆春鎮", "枋寮鄉"]
            },
            "臺東縣": {
                "three_days": "037", # F-D0047-037
                "weekly": "039", # F-D0047-039
                "district": ["長濱鄉", "海端鄉", "池上鄉", "成功鎮", "關山鎮", "東河鄉", "鹿野鄉", "延平鄉", "卑南鄉", "臺東市", "太麻里鄉", "綠島鄉", "達仁鄉", "大武鄉", "蘭嶼鄉", "金峰鄉"]
            },
            "花蓮縣": {
                "three_days": "041", # F-D0047-041
                "weekly": "043", # F-D0047-043
                "district": ["秀林鄉", "新城鄉", "花蓮市", "吉安鄉", "壽豐鄉", "萬榮鄉", "鳳林鎮", "豐濱鄉", "光復鄉", "卓溪鄉", "瑞穗鄉", "玉里鎮", "富里鄉"]
            },
            "澎湖縣": {
                "three_days": "045", # F-D0047-045
                "weekly": "047", # F-D0047-047
                "district": ["白沙鄉", "西嶼鄉", "湖西鄉", "馬公市", "望安鄉", "七美鄉"]
            },
            "基隆市": {
                "three_days": "049", # F-D0047-049
                "weekly": "051", # F-D0047-051
                "district": ["安樂區", "中山區", "中正區", "七堵區", "信義區", "仁愛區", "暖暖區"]
            },
            "新竹市": {
                "three_days": "053", # F-D0047-053
                "weekly": "055", # F-D0047-055
                "district": ["北區", "香山區", "東區"]
            },
            "嘉義市": {
                "three_days": "057", # F-D0047-057
                "weekly": "059", # F-D0047-059
                "district": ["東區", "西區"]
            },
            "臺北市": {
                "three_days": "061", # F-D0047-061
                "weekly": "063", # F-D0047-063
                "district": ["北投區", "士林區", "內湖區", "中山區", "大同區", "松山區", "南港區", "中正區", "萬華區", "信義區", "大安區", "文山區"]
            },
            "高雄市": {
                "three_days": "065", # F-D0047-065
                "weekly": "067", # F-D0047-067
                "district": ["楠梓區", "左營區", "三民區", "鼓山區", "苓雅區", "新興區", "前金區", "鹽埕區", "前鎮區", "旗津區", "小港區", "那瑪夏區", "甲仙區", "六龜區", "杉林區", "內門區", "茂林區", "美濃區", "旗山區", "田寮區", "湖內區", "茄萣區", "阿蓮區", "路竹區", "永安區", "岡山區", "燕巢區", "彌陀區", "橋頭區", "大樹區", "梓官區", "大社區", "仁武區", "鳥松區", "大寮區", "鳳山區", "林園區", "桃源區"]
            },
            "新北市": {
                "three_days": "069", # F-D0047-069
                "weekly": "071", # F-D0047-071
                "district": ["石門區", "三芝區", "金山區", "淡水區", "萬里區", "八里區", "汐止區", "林口區", "五股區", "瑞芳區", "蘆洲區", "雙溪區", "三重區", "貢寮區", "平溪區", "泰山區", "新莊區", "石碇區", "板橋區", "深坑區", "永和區", "樹林區", "中和區", "土城區", "新店區", "坪林區", "鶯歌區", "三峽區", "烏來區"]
            },
            "臺中市": {
                "three_days": "073", # F-D0047-073
                "weekly": "075", # F-D0047-075
                "district": ["北屯區", "西屯區", "北區", "南屯區", "西區", "東區", "中區", "南區", "和平區", "大甲區", "大安區", "外埔區", "后里區", "清水區", "東勢區", "神岡區", "龍井區", "石岡區", "豐原區", "梧棲區", "新社區", "沙鹿區", "大雅區", "潭子區", "大肚區", "太平區", "烏日區", "大里區", "霧峰區"]
            },
            "臺南市": {
                "three_days": "077", # F-D0047-077
                "weekly": "079", # F-D0047-079
                "district": ["安南區", "中西區", "安平區", "東區", "南區", "北區", "白河區", "後壁區", "鹽水區", "新營區", "東山區", "北門區", "柳營區", "學甲區", "下營區", "六甲區", "南化區", "將軍區", "楠西區", "麻豆區", "官田區", "佳里區", "大內區", "七股區", "玉井區", "善化區", "西港區", "山上區", "安定區", "新市區", "左鎮區", "新化區", "永康區", "歸仁區", "關廟區", "龍崎區", "仁德區"]
            },
            "連江縣": {
                "three_days": "081", # F-D0047-081
                "weekly": "083", # F-D0047-083
                "district": ["南竿鄉", "北竿鄉", "莒光鄉", "東引鄉"]
            },
            "金門縣": {
                "three_days": "085", # F-D0047-085
                "weekly": "087", # F-D0047-087
                "district": ["金城鎮", "金湖鎮", "金沙鎮", "金寧鄉", "烈嶼鄉", "烏坵鄉"]
            },
            "臺灣": {
                "three_days": "089", # F-D0047-089
                "weekly": "091", # F-D0047-091
                "district": ["宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣", "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市", "新竹縣", "新竹市", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣", "嘉義市", "屏東縣"]
            }
        }
    }
}

# 天氣狀況對應表
CONDITION_MAP = {
    "01": ATTR_CONDITION_SUNNY,        # 晴天
    "02": ATTR_CONDITION_SUNNY,        # 晴時多雲
    "03": ATTR_CONDITION_SUNNY,
    "04": ATTR_CONDITION_CLOUDY,       # 多雲
    "05": ATTR_CONDITION_CLOUDY,       # 多雲時陰
    "06": ATTR_CONDITION_CLOUDY,
    "07": ATTR_CONDITION_CLOUDY,       # 陰天
    # 8~23 都是下雨
    "08": ATTR_CONDITION_RAINY,        # 短暫陣雨
    "09": ATTR_CONDITION_RAINY,        # 多雲時陰短暫雨
    "10": ATTR_CONDITION_RAINY,        # 連續性陣雨
    "11": ATTR_CONDITION_RAINY,        # 雨天
    "12": ATTR_CONDITION_RAINY,
    "13": ATTR_CONDITION_RAINY,
    "14": ATTR_CONDITION_RAINY,
    "15": ATTR_CONDITION_RAINY,
    "16": ATTR_CONDITION_RAINY,
    "17": ATTR_CONDITION_RAINY,
    "18": ATTR_CONDITION_RAINY,
    "19": ATTR_CONDITION_RAINY,
    "20": ATTR_CONDITION_RAINY,
    "21": ATTR_CONDITION_RAINY,
    "22": ATTR_CONDITION_RAINY,
    "23": ATTR_CONDITION_RAINY,
    # 24~28 為有霧
    "24": ATTR_CONDITION_FOG,
    "25": ATTR_CONDITION_FOG,
    "26": ATTR_CONDITION_FOG,
    "27": ATTR_CONDITION_FOG,
    "28": ATTR_CONDITION_FOG,
    # 29~41 為有雨加有霧
    "29": ATTR_CONDITION_RAINY,
    "30": ATTR_CONDITION_RAINY,
    "31": ATTR_CONDITION_RAINY,
    "32": ATTR_CONDITION_RAINY,
    "33": ATTR_CONDITION_RAINY,
    "34": ATTR_CONDITION_RAINY,
    "35": ATTR_CONDITION_RAINY,
    "36": ATTR_CONDITION_RAINY,
    "37": ATTR_CONDITION_RAINY,
    "38": ATTR_CONDITION_RAINY,
    "39": ATTR_CONDITION_RAINY,
    "40": ATTR_CONDITION_RAINY,
    "41": ATTR_CONDITION_RAINY,
    "42": ATTR_CONDITION_SNOWY,        # 下雪
}
