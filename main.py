import cv2 #opencv kamerayı açmak ve görüntü işlemek için
import mediapipe as mp #El algılama
import pyautogui #Fare imlecini ekranda hareket ettirmek ve tıklama gibi işlemleri yapmak için
import os #Dosya ve klasör işlemleri için 
from datetime import datetime #Ekran görüntüsü tarihi
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QThread, pyqtSignal

cap = cv2.VideoCapture(0) #Kamerayı başlatır
hands = mp.solutions.hands.Hands() #MediaPipe, elleri algılamak için sınıf oluşturur.
draw = mp.solutions.drawing_utils #Ellerin ve parmakların ekranda çizilmesini sağlar
screen_w, screen_h = pyautogui.size() #Ekranın genişlik ve yüksekliğini alır

# Parmakların konumunu kontrol eden fonksiyon
def is_hand_open(landmarks):
    fingers = []
    # Baş parmak (x ekseni)
    fingers.append(landmarks[4].x > landmarks[3].x) #baş parmak açık mı kapalı mı, x ekseninde daha sağda mı diye bakıyor (aynalı)
    # Diğer parmaklar (y ekseni)
    tips = [8, 12, 16, 20]
    for tip in tips:
        fingers.append(landmarks[tip].y < landmarks[tip - 2].y) #işaret, orta, yüzük ve serçe parmaklar açık mı kapalı mı, boğumlara bakarak ucu daha yukarıdaysa (y ekseni küçükse), parmak açık sayılıyor
    return all(fingers)

while True:
    _, frame = cap.read() #Kameradan bir kare (fotoğraf) alır.
    frame = cv2.flip(frame, 1) #:Görüntüyü yatay çevirir (ayna efekti)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #MediaPipe RGB formatta çalıştığı için OpenCV’nin BGR formatını dönüştürüyoruz
    result = hands.process(rgb) #landmark denen noktaları bul (el,eklem)

    if result.multi_hand_landmarks: #El algılandıysa, her bir el için landmark (eklem) noktalarını sırayla alır
        for hand_landmarks in result.multi_hand_landmarks: 
            landmarks = hand_landmarks.landmark

            #21 parmak nokta var
            thumb_tip = landmarks[4] #4 numara baş parmak ucu
            index_tip = landmarks[8] #8 numaralı nokta işaret parmağının ucu
            x = int(index_tip.x * screen_w) #Bu noktanın x ve y koordinatları 0 ile 1 arasında olur
            y = int(index_tip.y * screen_h) #Biz bunları ekran boyutlarıyla çarparak gerçek ekrandaki fare konumuna dönüştürüyoruz


            
            distance = ((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)**0.5 # Parmaklar arası mesafeyi hesapla; index işaret parmağı ucu,thumb baş parmağın ucu (hipotenüs ile mesafe)
            if distance < 0.03:
                pyautogui.click()
                pyautogui.sleep(0.6)  # tıklama spamlamasın diye kısa beklet
            #print("Distance:", distance) # left click için deneme    
    
            pyautogui.moveTo(x, y) #Hesaplanan x ve y konumuna imleci taşı
            draw.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS) #Elin üzerine parmak eklemleri çizilir, böylece ekranda neyin takip edildiğini görürsün

            # EKRAN GÖRÜNTÜSÜ ALMA: EL TAMAMEN AÇIKSA
            if is_hand_open(landmarks):
                print("El açık olarak algılandı.")  # <-- Kontrol için eklendi
                
                #Ekran görüntüsü için dosya yolu kodları
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop") #Masaüstünde klasör yolu
                save_folder = os.path.join(desktop_path, "PythonEkranGoruntuleri")

                now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") #Ekran görüntüsüne tarihli isim
                filename = f"screenshot_{now}.png"
                full_path = os.path.join(save_folder, filename)

                pyautogui.screenshot(full_path) #Ekran görüntüsü alınarak belirtilen konum
                print("Ekran görüntüsü alındı:", full_path) 

                pyautogui.sleep(1.5) #Bekleme süresi

 
    cv2.imshow("Hand Tracking Mouse", frame) #Kameradan alınan görüntü gösterilir.

    if cv2.waitKey(1) == ord("q"):
        break

cap.release() #Kamera bağlantısı serbest bırakılır
cv2.destroyAllWindows() #Açık olan tüm OpenCV pencereleri kapatılır

