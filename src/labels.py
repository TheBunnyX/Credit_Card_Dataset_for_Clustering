"""Human-readable labels and texts (Thai + English) used by the web UI."""

# Inputs shown by default in the prediction form; the rest live under "advanced".
ESSENTIAL_FIELDS = [
    "BALANCE",
    "CREDIT_LIMIT",
    "PURCHASES",
    "PURCHASES_FREQUENCY",
    "CASH_ADVANCE",
    "CASH_ADVANCE_FREQUENCY",
    "PAYMENTS",
    "PRC_FULL_PAYMENT",
]

# column -> {"th": (label, hint), "en": (label, hint)}
FIELD_INFO = {
    "BALANCE": {"th": ("ยอดคงค้างในบัญชี", "ยอดเงินคงเหลือในบัญชีบัตร"),
                "en": ("Balance", "Amount left on the card account")},
    "BALANCE_FREQUENCY": {"th": ("ความถี่การอัปเดตยอด", "0 = แทบไม่เปลี่ยน, 1 = เปลี่ยนบ่อยมาก"),
                          "en": ("Balance update frequency", "0 = rarely updated, 1 = very often")},
    "PURCHASES": {"th": ("ยอดซื้อรวม", "มูลค่าการซื้อสินค้า/บริการทั้งหมดใน 6 เดือน"),
                  "en": ("Total purchases", "Value of all purchases over 6 months")},
    "ONEOFF_PURCHASES": {"th": ("ยอดซื้อครั้งเดียวจบ", "มูลค่าที่จ่ายเต็มจำนวนในครั้งเดียว (ไม่ผ่อน)"),
                         "en": ("One-off purchases", "Purchases paid in one go (no instalments)")},
    "INSTALLMENTS_PURCHASES": {"th": ("ยอดซื้อแบบผ่อน", "มูลค่าที่ซื้อด้วยการผ่อนชำระ"),
                               "en": ("Instalment purchases", "Purchases paid in instalments")},
    "CASH_ADVANCE": {"th": ("ยอดกดเงินสดล่วงหน้า", "จำนวนเงินสดที่กดจากบัตร"),
                     "en": ("Cash advance", "Cash withdrawn with the card")},
    "PURCHASES_FREQUENCY": {"th": ("ความถี่ในการซื้อ", "0 = แทบไม่ซื้อ, 1 = ซื้อบ่อยมาก"),
                            "en": ("Purchase frequency", "0 = almost never, 1 = very often")},
    "ONEOFF_PURCHASES_FREQUENCY": {"th": ("ความถี่ซื้อครั้งเดียวจบ", "0 = แทบไม่เคย, 1 = บ่อยมาก"),
                                   "en": ("One-off purchase frequency", "0 = almost never, 1 = very often")},
    "PURCHASES_INSTALLMENTS_FREQUENCY": {"th": ("ความถี่ซื้อแบบผ่อน", "0 = แทบไม่เคย, 1 = บ่อยมาก"),
                                         "en": ("Instalment purchase frequency", "0 = almost never, 1 = very often")},
    "CASH_ADVANCE_FREQUENCY": {"th": ("ความถี่กดเงินสด", "0 = แทบไม่กด, 1 = กดบ่อยมาก"),
                               "en": ("Cash advance frequency", "0 = almost never, 1 = very often")},
    "CASH_ADVANCE_TRX": {"th": ("จำนวนครั้งที่กดเงินสด", "จำนวนรายการกดเงินสด"),
                         "en": ("Cash advance transactions", "Number of cash withdrawals")},
    "PURCHASES_TRX": {"th": ("จำนวนครั้งที่ซื้อ", "จำนวนรายการซื้อ"),
                      "en": ("Purchase transactions", "Number of purchases")},
    "CREDIT_LIMIT": {"th": ("วงเงินบัตร", "วงเงินสูงสุดที่ได้รับ (เว้นว่างได้)"),
                     "en": ("Credit limit", "Card credit limit (optional)")},
    "PAYMENTS": {"th": ("ยอดที่ชำระแล้ว", "จำนวนเงินที่ลูกค้าชำระคืนทั้งหมด"),
                 "en": ("Payments", "Total amount paid back")},
    "MINIMUM_PAYMENTS": {"th": ("ยอดชำระขั้นต่ำ", "ยอดขั้นต่ำที่ชำระ (เว้นว่างได้)"),
                         "en": ("Minimum payments", "Minimum amount paid (optional)")},
    "PRC_FULL_PAYMENT": {"th": ("สัดส่วนที่จ่ายเต็มจำนวน", "0 = ไม่เคยจ่ายเต็ม, 1 = จ่ายเต็มทุกรอบ"),
                         "en": ("Full-payment ratio", "0 = never pays in full, 1 = always")},
    "TENURE": {"th": ("อายุบัตร (เดือน)", "ระยะเวลาที่ใช้บริการ (ข้อมูลมีช่วง 6-12 เดือน)"),
               "en": ("Tenure (months)", "Months as a customer (6-12 in this data)")},
}

# Short names used in "why this segment" explanations: column -> (th, en)
REASON_LABELS = {
    "BALANCE": ("ยอดคงค้าง", "Balance"),
    "PURCHASES": ("ยอดซื้อ", "Purchases"),
    "ONEOFF_PURCHASES": ("ยอดซื้อครั้งเดียวจบ", "One-off purchases"),
    "INSTALLMENTS_PURCHASES": ("ยอดซื้อแบบผ่อน", "Instalment purchases"),
    "CASH_ADVANCE": ("ยอดกดเงินสด", "Cash advance"),
    "CREDIT_LIMIT": ("วงเงิน", "Credit limit"),
    "PAYMENTS": ("ยอดชำระ", "Payments"),
    "PURCHASES_FREQUENCY": ("ความถี่ในการซื้อ", "Purchase frequency"),
    "CASH_ADVANCE_FREQUENCY": ("ความถี่กดเงินสด", "Cash advance frequency"),
    "PRC_FULL_PAYMENT": ("การจ่ายเต็มจำนวน", "Full-payment ratio"),
}

# (column, above-average th, below-average th, above-average en, below-average en)
TRAIT_DEFS = [
    ("BALANCE", "ยอดคงค้างสูง", "ยอดคงค้างต่ำ", "High balance", "Low balance"),
    ("PURCHASES", "ยอดซื้อสูง", "ยอดซื้อต่ำ", "High spending", "Low spending"),
    ("PURCHASES_FREQUENCY", "ซื้อบ่อย", "ซื้อน้อยครั้ง", "Buys often", "Rarely buys"),
    ("INSTALLMENTS_PURCHASES", "ผ่อนชำระมาก", "ผ่อนชำระน้อย", "Many instalments", "Few instalments"),
    ("CASH_ADVANCE", "กดเงินสดมาก", "แทบไม่กดเงินสด", "Heavy cash advance", "Rarely takes cash"),
    ("CREDIT_LIMIT", "วงเงินสูง", "วงเงินต่ำ", "High credit limit", "Low credit limit"),
    ("PAYMENTS", "ชำระคืนมาก", "ชำระคืนน้อย", "Pays back a lot", "Pays back little"),
    ("PRC_FULL_PAYMENT", "จ่ายเต็มจำนวนบ่อย", "ไม่ค่อยจ่ายเต็มจำนวน", "Often pays in full", "Rarely pays in full"),
]

# Short English "who they are" line per segment (the English strategy lives in src/segments.py).
DESC_EN = {
    "Cash Advance Users": "Hardly shop with the card but withdraw cash often and in large amounts, using the card like a loan.",
    "Big Spenders": "Spend a lot and often, with high limits, on both one-off and instalment purchases - the most valuable customers.",
    "Full Payers (Transactors)": "Use the card regularly, like instalments and often pay in full; low outstanding balance.",
    "Installment Shoppers": "Buy often and mostly pay in instalments.",
    "Revolvers": "High balance, mix cash advances with purchases and rarely pay in full - high interest income but default risk.",
    "Low Payers": "Pay back very little relative to usage and almost never in full - a group to watch.",
    "Low Activity": "Very low balance and purchases - possibly new users, students or a back-up card.",
    "Mainstream": "Moderate use, rarely pay in full, no stand-out behaviour.",
}

# name_th, who they are, what to do
SEGMENT_TH = {
    "Cash Advance Users": (
        "กลุ่มกดเงินสด",
        "แทบไม่ใช้บัตรจับจ่าย แต่กดเงินสดล่วงหน้าบ่อยและยอดสูง ใช้บัตรเหมือนวงเงินกู้",
        "เสนอสินเชื่อส่วนบุคคลหรือโอนยอดดอกเบี้ยต่ำแทนการกดเงินสด ลดค่าธรรมเนียมกดเงินสด "
        "กระตุ้นให้ใช้จ่ายผ่านบัตรด้วยแคชแบ็ก และติดตามความเสี่ยงเครดิตใกล้ชิด",
    ),
    "Big Spenders": (
        "กลุ่มนักช้อปยอดสูง",
        "ใช้จ่ายสูงและบ่อย วงเงินสูง ทั้งซื้อครั้งเดียวและผ่อน เป็นลูกค้ามูลค่าสูงสุด",
        "ให้สิทธิพิเศษระดับพรีเมียม แคชแบ็กยอดใหญ่ ปรับเพิ่มวงเงิน เน้นรักษาลูกค้าไว้มากกว่าหาลูกค้าใหม่",
    ),
    "Full Payers (Transactors)": (
        "กลุ่มใช้บ่อยและจ่ายเต็ม",
        "ใช้บัตรจ่ายสม่ำเสมอ ชอบผ่อน และชำระเต็มจำนวนบ่อย ยอดค้างต่ำ",
        "สะสมแต้มหรือจับมือร้านค้าพันธมิตร ส่งโปรผ่อน 0% (ท่องเที่ยว เครื่องใช้ไฟฟ้า สมาร์ทโฟน) "
        "รายได้หลักมาจากค่าธรรมเนียมร้านค้า ไม่ใช่ดอกเบี้ย จึงเน้นให้ใช้ต่อเนื่อง",
    ),
    "Installment Shoppers": (
        "กลุ่มนักผ่อน",
        "ซื้อบ่อยและเน้นผ่อนชำระเป็นหลัก",
        "ส่งโปรแกรมผ่อนดอกเบี้ยต่ำ/0% กับร้านค้าพันธมิตร (ท่องเที่ยว เครื่องใช้ในบ้าน อิเล็กทรอนิกส์)",
    ),
    "Revolvers": (
        "กลุ่มหมุนเงินและค้างชำระ",
        "ยอดค้างสูง กดเงินสดควบคู่กับการซื้อ และแทบไม่จ่ายเต็ม สร้างดอกเบี้ยสูงแต่เสี่ยงผิดนัด",
        "เสนอโอนหนี้/รวมหนี้ดอกเบี้ยต่ำ ตั้งหักบัญชีอัตโนมัติและแจ้งเตือนกำหนดชำระ พร้อมเฝ้าระวังความเสี่ยง",
    ),
    "Low Payers": (
        "กลุ่มชำระคืนน้อย",
        "ชำระคืนน้อยมากเมื่อเทียบกับการใช้งาน และแทบไม่เคยจ่ายเต็ม เป็นกลุ่มที่ควรระวัง",
        "ส่งการแจ้งเตือนชำระ ชวนสมัครหักบัญชีอัตโนมัติ ติดตามทวงถามตั้งแต่เนิ่น ๆ และทบทวนวงเงิน",
    ),
    "Low Activity": (
        "กลุ่มใช้งานน้อย",
        "ยอดคงค้างและการซื้อต่ำมาก อาจเป็นผู้ใช้ใหม่ นักศึกษา หรือถือบัตรไว้สำรอง",
        "ทำแคมเปญกระตุ้นการใช้ เช่น โบนัสเมื่อสมัคร แคชแบ็กการซื้อครั้งแรก "
        "หรือเสนอบัตรระดับเริ่มต้น ยกเว้นค่าธรรมเนียม และให้รางวัลเมื่อชำระตรงเวลา",
    ),
    "Mainstream": (
        "กลุ่มทั่วไป",
        "ใช้งานระดับปานกลาง จ่ายเต็มไม่บ่อย ไม่มีลักษณะเด่นชัด",
        "ส่งข้อเสนอตามหมวดที่ใช้จ่าย ขายประกันหรือผลิตภัณฑ์ออม และชวนให้ใช้โปรผ่อน",
    ),
}

# Business bucket per segment, used for the executive summary on the overview tab.
#   value = most profitable / engaged, watch = credit-risk to monitor, grow = under-used, worth activating
SEGMENT_GROUP = {
    "Big Spenders": "value",
    "Full Payers (Transactors)": "value",
    "Installment Shoppers": "value",
    "Revolvers": "watch",
    "Low Payers": "watch",
    "Cash Advance Users": "watch",
    "Low Activity": "grow",
    "Mainstream": "grow",
}

# Plain-language description of each algorithm compared on the "Why this method" tab.
ALGO_INFO = {
    "kmeans": {
        "name": "K-Means",
        "how_th": "ตั้ง \"จุดนัดพบ\" ไว้ k จุด ให้ลูกค้าแต่ละคนไปรวมที่จุดที่ใกล้ที่สุด แล้วขยับจุดไปไว้ตรงกลางกลุ่ม ทำซ้ำจนนิ่ง",
        "how_en": "Place k \"meeting points\", send each customer to the nearest one, move each point to the middle of its group, repeat until stable.",
        "pros_th": "ผลคงที่ เร็ว จัดลูกค้าใหม่ได้ทันที อธิบายง่ายด้วยลูกค้าต้นแบบของแต่ละกลุ่ม",
        "pros_en": "Stable, fast, places new customers instantly, easy to explain with a typical customer per group.",
        "cons_th": "ต้องกำหนดจำนวนกลุ่มเอง และถนัดกลุ่มที่มีขนาดใกล้เคียงกัน",
        "cons_en": "You must choose the number of groups; works best when groups are similar in size and shape.",
    },
    "hierarchical": {
        "name": "Hierarchical (Ward)",
        "how_th": "เหมือนทำแผนผังตระกูล: จับคู่ลูกค้าที่คล้ายกันที่สุดรวมกันทีละขั้น จนได้ต้นไม้ แล้วตัดต้นไม้ให้เหลือ k กลุ่ม",
        "how_en": "Like a family tree: repeatedly merge the two most similar groups until everything is one tree, then cut it into k groups.",
        "pros_th": "เห็นว่ากลุ่มไหนใกล้กัน (dendrogram) ไม่มีการสุ่ม",
        "pros_en": "Shows which groups are related (dendrogram); no randomness.",
        "cons_th": "ผลเปลี่ยนมากเมื่อข้อมูลเปลี่ยนเล็กน้อย จัดลูกค้าใหม่โดยตรงไม่ได้ และช้าเมื่อข้อมูลเยอะ",
        "cons_en": "Changes a lot when the data changes slightly, cannot place new customers directly, slow on big data.",
    },
    "gmm": {
        "name": "Gaussian Mixture",
        "how_th": "คล้าย K-Means แต่ให้แต่ละกลุ่มมีรูปร่างและขนาดต่างกันได้ และบอกเป็นความน่าจะเป็นว่าอยู่กลุ่มไหน",
        "how_en": "Like K-Means but each group may have its own shape and size, and membership is given as probabilities.",
        "pros_th": "ยืดหยุ่น ให้ความน่าจะเป็นของแต่ละกลุ่ม",
        "pros_en": "Flexible, gives a probability for each group.",
        "cons_th": "ในข้อมูลนี้กลุ่มทับซ้อนกันมากและผลแกว่งตามการสุ่ม",
        "cons_en": "On this data the groups overlap heavily and results vary between runs.",
    },
    "dbscan": {
        "name": "DBSCAN",
        "how_th": "หากลุ่มจากความหนาแน่น: ที่ไหนลูกค้าอยู่กันแน่นถือเป็นกลุ่ม ใครอยู่โดดเดี่ยวถือเป็นค่าผิดปกติ",
        "how_en": "Finds groups by density: crowded areas become groups, isolated customers are marked as outliers.",
        "pros_th": "ไม่ต้องกำหนดจำนวนกลุ่ม และหาลูกค้าผิดปกติได้",
        "pros_en": "No need to choose the number of groups; finds unusual customers.",
        "cons_th": "ลูกค้าในข้อมูลนี้กระจายต่อเนื่อง จึงได้ก้อนใหญ่ก้อนเดียวกับ \"ค่าผิดปกติ\" จำนวนมาก ใช้ทำการตลาดไม่ได้",
        "cons_en": "Customers here are spread continuously, so it finds one big blob plus many \"outliers\" - not usable for marketing.",
    },
}

# One colour per segment slot (colour-blind friendly), reused by the chart, cards and map.
PALETTE = ["#3b6cf0", "#e8710a", "#1a9e6f", "#d6336c", "#7b4fd6", "#a07800", "#0e8aa6", "#6b7686"]
