# STM32KBTx Kartları İçin Timer Kullanarak ve Periyodunu Değiştirerek GPIO Sinyali Gönderme Yazılımı

Bu yazılım ile Modbus protokolünü kullanarak bilgisayarınızdan STM32 cihazınıza master olarak veriler gönderip, cihazın Timerının(TIM3) periyodunu değiştirebilirsiniz. Cihaz LED ışığını belirlenen periyotta yanıp söndürecek ve yine aynı periyotta PA0 GPIO çıkışına yüksek ve düşük sinyal gönderecektir.

## Cihaza Kurulum ve Çalıştırma

	1. Elinizdeki kartın SMT32KBTx modellerinden biri olduğuna ve kullandığınız kablonun veri aktarımını desteklediğinden emin olun.

	2. STM32CubeIDE uygulamasını indirin, çalıştırın ve cihazı bilgisayara bağlayın.

	3. File -> Open Projects From File System menüsünden proje dizinini seçin ve projeyi uygulamada açın.

	4. modbusSlave.h header dosyasındaki SLAVE_ID değerini istediğiniz SLAVE_ID değerine göre ayarlayın(İlk değeri 7'dir).

	5. Proje açıkken uygulama içerisinde üstteki çalıştır veya debug butonu aracılığıyla projeyi buildleyip cihaza flashlayın. (Debug modunda çalıştırdıysanız üstteki devam butonundan breakpointlerde ilerletmeniz gerekiyor.)

	6. Şu ana kadar bir sorun çıkmadıysa artık cihazın LED ışığı yanıp sönmeye başlar ve Modbus protokolünü kullanarak periyodunu değiştirebilirsiniz.

## Kullanılabilir Fonksiyonlar
### <u>setFrequency(Fonksiyon Kodu: 0x0B)</u>:

Bu fonksiyonu kullanarak cihazdaki TIM3 timerının periyodunu istediğiniz bir değere ayarlayabilirsiniz. Bu değer milisaniye cinsinden verilir.

**İstek(Request) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID (0x0B)<br>
4 Bytes -> Milisaniye cinsinden istenen periyot.<br>
2 Bytes -> CRC

Bu fonksiyon bir veri döndürmez ve eğer doğru mesajı gönderdiyseniz sonucu LED ışığının yanıp sönme hızından veya PA0 çıkışındaki sinyalden anlayabilirsiniz.

**Örnek Request Mesajı** -> 07 0B 000001F4 7AA4<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihazdan<br>
-> 0B ID'li fonksiyonu çağırıyoruz.<br>
-> TIM3 timerını 000001F4 değerine eşitlemek istiyoruz.<br>
-> Son olarak hesapladığımız 7AA4 CRC değerini mesaja ekliyoruz.