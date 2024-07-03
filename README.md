# STM32 Modbus Master GUI

**DİKKAT:** Bu yazılım sadece macOS/Linux port sistemleri için yapılmıştır. Farklı platformlar için kod içerisinde port seçimi için değişiklik gerekiyor.

Bu yazılım sayesinde Modbus protokolünü kullanarak 10 adete kadar STM32 slave cihazların içerisinde bulunan sıcaklık verisi görüntülenebilir.

## Kullanım Talimatları

- Uygulama içerisinde üst kısımdaki port menüsünden cihazlarınızın bağlı olduğu portu ve uygun Baud Rate'i seçin ve 'Connect' butonuna tıklayın.
- 'Not Connected' ibaresi 'Connected' a dönüştüğünde artık veri sorgulayabilirsiniz.
- 10 adet kutucuktaki Slave ID'leri belirleyin ve aşağıdan kaç saniyede bir veri okumak istediğinize göre Interval seçeneği belirleyin.
- 'Start Reading Temperature' butonuna tıkladığınızda artık seçtiğiniz zaman aralığında verilerin ilgili kutucukların sağında görebilirsiniz.