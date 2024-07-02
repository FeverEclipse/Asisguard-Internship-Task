\mainpage STM32 Modbus Slave

# STM32KBTx Kartları İçin Modbus RTU Slave Yazılımı

Bu yazılım ile Modbus protokolünü kullanarak bilgisayarınızdan STM32 cihazınıza master olarak veriler gönderip, cihaz ile iletişime geçebilirsiniz. Modbus protokolünde tanımlı standart fonksiyonlara ek olarak özel tanımlanmış fonksiyonlar ile ek işlevler yapabilirsiniz.

## Cihaza Kurulum ve Çalıştırma

	1. Elinizdeki kartın SMT32KBTx modellerinden biri olduğuna ve kullandığınız kablonun veri aktarımını desteklediğinden emin olun.

	2. STM32CubeIDE uygulamasını indirin, çalıştırın ve cihazı bilgisayara bağlayın.

	3. File -> Open Projects From File System menüsünden proje dizinini seçin ve projeyi uygulamada açın.

	4. modbusSlave.h header dosyasındaki SLAVE_ID değerini istediğiniz SLAVE_ID değerine göre ayarlayın.

	5. Proje açıkken uygulama içerisinde üstteki çalıştır veya debug butonu aracılığıyla projeyi buildleyip cihaza flashlayın. (Debug modunda çalıştırdıysanız üstteki devam butonundan breakpointlerde ilerletmeniz gerekiyor.)

	6. Şu ana kadar bir sorun çıkmadıysa artık cihaz ile Modbus protokolünü kullanarak iletişim kurabilirsiniz.

## Kullanılabilir Fonksiyonlar
### <u>readHoldingRegs(Fonksiyon Kodu: 0x03)</u>:

**Holding Registers Ön Bilgi:**<br> Holding Registerlar cihaz içindeki 50 adet her biri 2 byte büyüklüğündeki serbest değişkenlerdir ve dışarıdan okuma/yazma yetkisine sahiptir. Geçiçi değerler veya ileride değiştirmeniz gereken değerler için kullanılabilir.
<br><br><br>
Bu fonksiyonu kullanarak cihazdaki Holding_Registers_Database listesinde bulunan 50 elemandan belirttiğiniz sıradan(index) başlayarak ve belirttiğiniz sayı kadarını okuyabilirsiniz.

**İstek(Request) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID (0x03)<br>
2 Bytes -> Starting Address / Başlangıç Adresi(index)<br>
2 Bytes -> Number of Registers to Read / Okunmak İstenen Register Sayısı<br>
2 Bytes -> CRC

**Yanıt(Response) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID(0x03)<br>
1 Byte -> Byte Count / Mesajdaki Byte Sayısı(N tane)<br>
N * 2 Byte -> Data / Veri<br>
2 Bytes -> CRC

**Örnek Request Mesajı** -> 07 03 0001 0002 AD95<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihazdan<br>
-> 03 ID'li fonksiyonu çağırıyoruz.<br>
-> 0001.sıradaki(index) değerden başlayarak,<br>
-> 0002 tane değer talep ediyoruz.<br>
-> Son olarak hesapladığımız AD95 CRC değerini mesaja ekliyoruz.

**Örnek Response Mesajı** -> 07 03 04 0200 08AE F71B<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihaz,<br>
-> 03 ID'li fonksiyonun yanıtını veriyor.<br>
-> 04 Bytelık, yani iki registerlık bir veri gönderecek<br>
-> 0200 bu registerların ilki,<br>
-> 08AE ise bu registerların ikincisi oluyor.<br>
-> Son olarak mesaja hesapladığı F71B CRC değerini ekliyor.

### <u>readInputRegs(Fonksiyon Kodu: 0x04)</u>:
**Input Registers Ön Bilgi:**<br> Input Registerlar cihaz içindeki 50 adet her biri 2 byte büyüklüğündeki özel değişkenlerdir ve dışarıdan yalnızca okuma yetkisine sahiptir. Cihaz içindeki sensör verileri ve cihaza gömülecek sabit değişkenler için kullanılabilir. Bu listenin ilk registerı sıcaklık sensörü verisine ayrılmıştır.
<br><br><br>
Bu fonksiyonu kullanarak cihazdaki Input_Registers_Database listesinde bulunan 50 elemandan belirttiğiniz sıradan(index) başlayarak ve belirttiğiniz sayı kadarını okuyabilirsiniz.

**İstek(Request) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID (0x04)<br>
2 Bytes -> Starting Address / Başlangıç Adresi(index)<br>
2 Bytes -> Number of Registers to Read / Okunmak İstenen Register Sayısı<br>
2 Bytes -> CRC

**Yanıt(Response) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID(0x04)<br>
1 Byte -> Byte Count / Mesajdaki Byte Sayısı(N tane)<br>
N * 2 Byte -> Data / Veri<br>
2 Bytes -> CRC

**Örnek Request Mesajı** -> 07 04 0001 0002 6D20<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihazdan<br>
-> 04 ID'li fonksiyonu çağırıyoruz.<br>
-> 0001.sıradaki(index) değerden başlayarak,<br>
-> 0002 tane değer talep ediyoruz.<br>
-> Son olarak hesapladığımız 6D20 CRC değerini mesaja ekliyoruz.

**Örnek Response Mesajı** -> 07 04 04 0457 08AE 18AB<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihaz,<br>
-> 04 ID'li fonksiyonun yanıtını veriyor.<br>
-> 04 Bytelık, yani iki registerlık bir veri gönderecek<br>
-> 0457 bu registerların ilki,<br>
-> 08AE ise bu registerların ikincisi oluyor.<br>
-> Son olarak mesaja hesapladığı 18AB CRC değerini ekliyor.

### <u>writeSingleReg(Fonksiyon Kodu: 0x06)</u>:

Bu fonksiyonu kullanarak cihazdaki Holding_Registers_Database listesinde belirttiğiniz sıraya(index) bir değer yazabilirsiniz.

**İstek(Request) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID (0x06)<br>
2 Bytes -> Register Address / Register sırası(index)<br>
2 Bytes -> Data / Registera yazılacak veri<br>
2 Bytes -> CRC

**Yanıt(Response) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID(0x06)<br>
2 Bytes -> Register Address / Register sırası(index)<br>
2 Bytes -> Data / Registerın değiştirilmiş değeri.<br>
2 Bytes -> CRC

**Örnek Request Mesajı** -> 07 06 0001 0032 B959<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihazdan<br>
-> 06 ID'li fonksiyonu çağırıyoruz.<br>
-> 0001.sıradaki(index) register'a<br>
-> 0032 değerini yazıyoruz.<br>
-> Son olarak hesapladığımız B959 CRC değerini mesaja ekliyoruz.

**Örnek Response Mesajı** -> 07 06 0001 0032 B959<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihaz,<br>
-> 06 ID'li fonksiyonun yanıtını veriyor.<br>
-> 0001.sıradaki(index) registerın güncellenmiş değerini<br>
-> 0032 olarak veriyor.<br>
-> Son olarak mesaja hesapladığı B959 CRC değerini ekliyor.

## Özel(Custom) Fonksiyonlar

### <u>incrementRegByOne(Fonksiyon Kodu: 0x07)</u>:

Bu fonksiyonu kullanarak cihazdaki Holding_Registers_Database listesindeki istediğiniz sıradaki(index) register'ın değerini 1 artırabilirsiniz.

**İstek(Request) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID (0x07)<br>
2 Bytes -> Register Address / Register sırası(index)<br>
2 Bytes -> CRC

**Yanıt(Response) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID(0x07)<br>
2 Bytes -> Register Address / Register sırası(index)<br>
2 Bytes -> Data / Registerın değiştirilmiş değeri.<br>
2 Bytes -> CRC

**Örnek Request Mesajı** -> 07 07 0003 90F0<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihazdan<br>
-> 07 ID'li fonksiyonu çağırıyoruz.<br>
-> 0003.sıradaki(index) register'ın değerini 1 artırmak istiyoruz.<br>
-> Son olarak hesapladığımız 90F0 CRC değerini mesaja ekliyoruz.

**Örnek Response Mesajı** -> 07 07 0003 0007 AE05<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihaz,<br>
-> 07 ID'li fonksiyonun yanıtını veriyor.<br>
-> 0003.sıradaki(index) registerın güncellenmiş değerini<br>
-> 0007 olarak veriyor.<br>
-> Son olarak mesaja hesapladığı AE05 CRC değerini ekliyor.

### <u>decrementRegByOne(Fonksiyon Kodu: 0x09)</u>:

Bu fonksiyonu kullanarak cihazdaki Holding_Registers_Database listesindeki istediğiniz sıradaki(index) register'ın değerini 1 eksiltebilirsiniz.

**İstek(Request) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID (0x09)<br>
2 Bytes -> Register Address / Register sırası(index)<br>
2 Bytes -> CRC

**Yanıt(Response) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID(0x09)<br>
2 Bytes -> Register Address / Register sırası(index)<br>
2 Bytes -> Data / Registerın değiştirilmiş değeri.<br>
2 Bytes -> CRC

**Örnek Request Mesajı** -> 07 09 0003 5391<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihazdan<br>
-> 09 ID'li fonksiyonu çağırıyoruz.<br>
-> 0003.sıradaki(index) register'ın değerini 1 azaltmak istiyoruz.<br>
-> Son olarak hesapladığımız 5391 CRC değerini mesaja ekliyoruz.

**Örnek Response Mesajı** -> 07 09 0003 0D02 FCA8<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihaz,<br>
-> 09 ID'li fonksiyonun yanıtını veriyor.<br>
-> 0003.sıradaki(index) registerın güncellenmiş değerini<br>
-> 0D02 olarak veriyor.<br>
-> Son olarak mesaja hesapladığı FCA8 CRC değerini ekliyor.

### <u>readTemp(Fonksiyon Kodu: 0x0A)</u>:

Bu fonksiyonu kullanarak cihaz üzerindeki sıcaklık sensörü verisini okuyabilirsiniz.

**İstek(Request) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID (0x0A)<br>
2 Bytes -> CRC

**Yanıt(Response) Byte Yapısı:**

1 Byte -> Slave ID<br>
1 Byte -> Function ID(0x0A)<br>
1 Byte -> Temp Value / Sıcaklık Değeri<br>
2 Bytes -> CRC

**Örnek Request Mesajı** -> 07 0A 8783<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihazdan<br>
-> 0A ID'li fonksiyonu çağırıyoruz.<br>
-> Son olarak hesapladığımız 8783 CRC değerini mesaja ekliyoruz.

**Örnek Response Mesajı** -> 07 0A 11 AD06<br>
Bu mesajı şöyle açıklayabiliriz:<br>
-> 07 Slave ID'sine sahip olan cihaz,<br>
-> 0A ID'li fonksiyonun yanıtını veriyor.<br>
-> Hexadecimal olarak sıcaklık değerini 11 olarak veriyor.
-> Son olarak mesaja hesapladığı AD06 CRC değerini ekliyor.

## Hata Kodları

Cihaz ile olan iletişimde birtakım sorunlar meydana gelebilir. Bunların ne olduğunu cihazdan gelen mesajdan anlayabilirsiniz.

Bunun için cihazdan gelen yanıt mesajındaki Fonksiyon ID'sine yani ikinci byte verisine bakın. Eğer higher byte 8 ise(Fonksiyon ID 0x8 ile başlıyorsa, örneğin 0x83) bu cihaz tarafından isteğinizin gerçekleştirilemediği anlamına gelir.

Hatanın ne olduğunu anlamak için gelen mesajdaki Exception ID'ye yani üçüncü byte verisine bakın. Hata kodları şöyledir:

- **0x01 - Illegal Function:** <br>
Gönderdiğiniz mesajdaki fonksiyon ID'si tanımlanamadı. Fonksiyon ID'sini kontrol edin.
- **0x02 - Illegal Data Address:**<br>
Gönderdiğiniz mesajdaki adres sırası(index) belirlenen sınırların dışında. Register listeleri 50 öge ile sınırlıdır. Buna göre mesajınızdaki adresi kontrol edin.
- **0x03 - Illegal Data Value:**<br>
Gönderdiğiniz mesajdaki talep ettiğiniz register sayısı sınırların dışında. Kaç tane register talep ettiğinizi kontrol edin.
- **0x04 - Illegal CRC:**<br>
Gönderdiğiniz mesajdaki son 2 byte olan CRC değeri cihazın hesapladığı CRC değeriyle uyuşmuyor. Mesajınızdaki CRC değerini hesaplamak için CRC16-Modbus algoritmasını kullandığınızdan emin olun.
