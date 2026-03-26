# Kỹ thuật chẩn đoán & sửa máy sấy tóc (nội bộ)

## An toàn bắt buộc
- Rút phích cắm trước khi kiểm tra/mở máy. Không đo đạc khi còn cấp điện nếu không có chuyên môn.
- Chờ máy nguội hẳn trước khi tháo vỏ; tránh bỏng nhiệt ở buồng nhiệt và điện trở.
- Nếu có mùi khét nặng, khói, tia lửa, hoặc vỏ biến dạng: **ngừng sử dụng ngay**.
- Với máy còn bảo hành/tem niêm phong: ưu tiên **bảo hành** thay vì tự mở.

## Cấu phần thường gặp (để định hướng)
- Dây nguồn + phích cắm
- Công tắc mức gió/nhiệt (slider/rocker)
- Cầu chì nhiệt (thermal fuse) / rơ-le nhiệt (thermostat/bimetal)
- Điện trở nhiệt (heater coil) và buồng nhiệt
- Motor + quạt (fan), chổi than (nếu motor DC có chổi than)
- Mạch điều khiển (diode/triac/IC) với dòng máy có nhiều mức
- Lưới lọc/miệng hút gió (tắc bụi gây quá nhiệt)

## Triệu chứng → Nguyên nhân → Checklist kiểm tra

### 1) Không lên nguồn (bấm không chạy, không quạt, không nóng)
**Nguyên nhân khả dĩ**
- Đứt dây nguồn/tiếp xúc kém ở phích cắm hoặc điểm gập.
- Công tắc hỏng/tiếp điểm cháy.
- Cầu chì nhiệt đứt do quá nhiệt.
- (Ít gặp) motor kẹt cháy hoặc mạch điều khiển hỏng.

**Checklist chẩn đoán (an toàn, ưu tiên không mở máy)**
1. Đổi ổ cắm khác, kiểm tra CB/aptomat.
2. Lắc nhẹ dây ở gần tay cầm/phích cắm (đã rút điện) xem có dấu hiệu lỏng/đứt gãy.
3. Quan sát mùi khét/vết cháy ở phích cắm và thân máy.

**Checklist chẩn đoán (khi mở máy - kỹ thuật viên)**
1. Đo thông mạch dây nguồn (continuity).
2. Đo thông mạch qua công tắc từng nấc.
3. Đo cầu chì nhiệt (thermal fuse): nếu hở mạch -> nghi đứt.
4. Nếu dây/công tắc/cầu chì OK: kiểm tra motor (kẹt trục/đứt cuộn) và mạch điều khiển.

**Hướng sửa phổ biến**
- Thay dây nguồn/đầu cắm nếu đứt gãy.
- Vệ sinh/thay công tắc nếu cháy tiếp điểm.
- Thay cầu chì nhiệt đúng nhiệt độ định mức (không đấu tắt).

### 2) Có gió nhưng không nóng (quạt chạy, không ra hơi nóng)
**Nguyên nhân khả dĩ**
- Điện trở nhiệt (heater coil) đứt.
- Cầu chì nhiệt/thermostat ngắt do quá nhiệt hoặc đã hỏng.
- Công tắc nhiệt hỏng ở nấc nhiệt.
- Mạch điều khiển/diode/triac lỗi (dòng nhiều mức).

**Checklist chẩn đoán**
1. Thử đổi mức nhiệt khác (nếu có) để xác định hỏng theo nấc.
2. Kiểm tra lưới hút gió có bị nghẹt bụi/tóc không.
3. (Kỹ thuật) Đo điện trở heater coil, cầu chì nhiệt, thermostat.

**Hướng sửa phổ biến**
- Vệ sinh lưới lọc/đường gió.
- Thay điện trở nhiệt (cuộn đốt) nếu đứt.
- Thay cầu chì nhiệt/thermostat nếu hở mạch.

### 3) Nóng yếu, lúc nóng lúc không / tự ngắt khi dùng vài phút
**Nguyên nhân khả dĩ**
- Tắc gió do bụi/tóc → quá nhiệt → thermostat ngắt.
- Quạt yếu (kẹt, bạc đạn khô, cánh quạt bám bụi) → giảm lưu lượng.
- Thermostat lão hóa, nhạy quá mức.
- Điện áp thấp (ổ cắm lỏng, dây nối dài kém).

**Checklist chẩn đoán**
1. Vệ sinh lưới hút gió, đảm bảo thông thoáng.
2. Không dùng dây nối dài rẻ/ổ cắm lỏng; thử ổ cắm khác.
3. Nghe tiếng quạt: có yếu/rục rịch/kẹt không.
4. (Kỹ thuật) Kiểm tra thermostat, motor, bạc đạn.

**Hướng sửa phổ biến**
- Vệ sinh đường gió + thay lưới lọc nếu biến dạng.
- Vệ sinh/bôi trơn/thay motor hoặc bạc đạn (tùy dòng).
- Thay thermostat nếu ngắt bất thường.

### 4) Có mùi khét / khói nhẹ / tia lửa ở cổ góp (nếu có)
**Nguyên nhân khả dĩ**
- Bụi/tóc cháy trong buồng nhiệt.
- Dây/tiếp điểm công tắc nóng chảy.
- Chổi than mòn (motor chổi than) gây tia lửa mạnh.
- Cuộn dây motor/điện trở bị chập nóng.

**Checklist chẩn đoán**
1. Ngừng dùng ngay, rút điện, chờ nguội.
2. Kiểm tra lưới lọc và buồng nhiệt có tóc/bụi bám.
3. (Kỹ thuật) Kiểm tra công tắc/đầu cos có cháy xém; kiểm tra chổi than và cổ góp.

**Hướng xử lý**
- Vệ sinh sâu buồng nhiệt và đường gió.
- Thay công tắc/đầu cos bị cháy.
- Thay chổi than (nếu có) và vệ sinh cổ góp; nếu cháy nặng → thay motor.
- Nếu nghi chập cháy cuộn → khuyến nghị thay cụm/đem bảo hành.

### 5) Kêu to, rung mạnh, gió yếu
**Nguyên nhân khả dĩ**
- Cánh quạt bám tóc/bụi, mất cân bằng.
- Kẹt dị vật trong quạt.
- Bạc đạn/ổ trục mòn.

**Checklist chẩn đoán**
1. Rút điện, kiểm tra miệng hút/xả có dị vật.
2. Vệ sinh tóc/bụi bám ở lưới và cánh quạt (nếu tiếp cận được).
3. (Kỹ thuật) Kiểm tra độ rơ trục, bạc đạn.

**Hướng sửa**
- Vệ sinh/loại bỏ dị vật.
- Thay bạc đạn/đổi motor nếu mòn nặng.

## Khi nào khuyến nghị bảo hành/đem trung tâm
- Máy còn bảo hành/tem niêm phong.
- Có khói, cháy xém, mùi khét nặng, vỏ biến dạng.
- Nghi chập cháy cuộn motor/điện trở, hoặc mạch điều khiển phức tạp.

