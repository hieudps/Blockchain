# Xay dung mang Blockchain bang Python

Du an mo phong mot blockchain don gian bang Python, Flask, HTML, CSS, JavaScript va Chart.js. Phien ban nang cap bo sung vi demo, luu du lieu JSON, validate chain, tamper block, gas fee, mining reward va dashboard truc quan.

## Phan tich he thong hien tai

Truoc khi nang cap, he thong da co cac thanh phan cot loi:

- Tao giao dich va dua vao danh sach pending transactions.
- Mining block bang Proof of Work.
- Tao hash block bang SHA-256.
- Block gom `index`, `timestamp`, `transactions`, `previous_hash`, `nonce`, `hash`.
- Smart Contract mo phong token theo mo hinh account-based.
- Kiem tra so du address.
- Xem danh sach block nhu Blockchain Explorer.
- Dashboard co bieu do co ban bang Chart.js.

Han che cua phien ban cu:

- Chua co co che tao vi va dang nhap vi.
- Du lieu mat khi tat server.
- Miner mac dinh co dinh, reward chua the hien ro.
- Chua co gas fee.
- Chua co validate chain va demo sua du lieu block.
- Dashboard va explorer con it thong tin.

## Chuc nang nang cap

### Tao vi moi

Nguoi dung co the tao vi moi bang nut `Create Wallet`. Dia chi vi duoc sinh tu UUID va SHA-256, giup moi vi co chuoi dinh danh gan nhu khong trung lap. Vi demo duoc cap so du ban dau de sinh vien de thuc hien giao dich khi demo.

### Dang nhap vi mo phong

Nguoi dung nhap dia chi vi de dang nhap. He thong luu vi hien tai va tu dong dung vi do lam sender khi gui giao dich. Chuc nang nay khong xu ly mat khau hay khoa rieng vi muc tieu la mo phong co che vi blockchain o muc do sinh vien.

### Lich su giao dich theo address

API `/api/address/<address>/transactions` quet toan bo chain va pending pool de lay cac giao dich gui di, nhan vao, reward, so token, gas fee, thoi gian va block chua giao dich. Chuc nang nay giup he thong giong Blockchain Explorer hon.

### Kiem tra tinh hop le blockchain

Nut `Validate Blockchain` kiem tra ba dieu kien:

- Hash hien tai cua block co dung voi du lieu block hay khong.
- `previous_hash` cua block sau co khop hash cua block truoc hay khong.
- Block da mine co thoa man difficulty Proof of Work hay khong.

Neu hop le, he thong hien thi `Blockchain hop le`. Neu sai, he thong chi ra block gap loi.

### Tamper block chung minh tinh bat bien

Chuc nang `Tamper Block` cho phep sua du lieu mot block da mine. He thong co tinh khong tinh lai hash. Khi validate lai, hash khong con khop voi du lieu block, tu do chung minh blockchain co tinh bat bien va de phat hien thay doi trai phep.

### Luu du lieu JSON

Du lieu duoc luu trong thu muc `data/`:

- `blockchain_data.json`: chain, pending transactions, difficulty, gas fee, mining reward.
- `wallets.json`: danh sach vi da tao.
- `balances.json`: so du token cua cac address.

Khi khoi dong lai Flask server, he thong tu dong load lai du lieu cu.

### Gas fee va mining reward

Khi gui giao dich, sender phai co du `amount + gas_fee`. Gas fee mac dinh la 1 token. Khi miner dao block thanh cong, miner nhan `mining_reward + tong gas fee` cua cac giao dich trong block. Reward transaction duoc ghi vao block de de quan sat.

### Dashboard nang cao

Dashboard hien thi:

- Total Blocks.
- Total Transactions.
- Pending Transactions.
- Total Wallets.
- Difficulty.
- Mining Reward.
- Bieu do so block theo thoi gian.
- Bieu do so giao dich trong moi block.
- Bieu do so du cua cac vi.

## API bo sung

| Method | API | Chuc nang |
| --- | --- | --- |
| POST | `/api/wallet/create` | Tao vi moi |
| GET | `/api/wallets` | Lay danh sach vi |
| POST | `/api/wallet/login` | Dang nhap vi mo phong |
| POST | `/api/transaction` | Them giao dich vao pending pool |
| POST | `/api/mine` | Mining block voi dia chi miner |
| GET | `/api/address/<address>/transactions` | Lay lich su giao dich cua address |
| GET | `/api/validate` | Kiem tra blockchain hop le |
| POST | `/api/tamper` | Sua du lieu block de demo tinh bat bien |
| POST | `/api/reset` | Reset blockchain |
| POST | `/api/settings/difficulty` | Cap nhat difficulty |
| GET | `/api/stats/advanced` | Lay thong ke nang cao |

## Cau truc thu muc

```text
blockchain_project/
|-- app.py
|-- blockchain.py
|-- smart_contract.py
|-- wallet.py
|-- storage.py
|-- config.py
|-- data/
|   |-- blockchain_data.json
|   |-- wallets.json
|   `-- balances.json
|-- templates/
|   |-- index.html
|   `-- block.html
|-- static/
|   |-- css/
|   |   `-- style.css
|   `-- js/
|       `-- main.js
|-- requirements.txt
`-- README.md
```

## Huong dan chay

1. Cai thu vien:

```bash
pip install -r requirements.txt
```

2. Chay Flask server:

```bash
python app.py
```

3. Mo trinh duyet:

```text
http://127.0.0.1:5000
```

4. Demo goi y:

- Tao 2 vi moi.
- Dang nhap vi thu nhat.
- Gui token sang vi thu hai.
- Mine block voi dia chi miner.
- Tim lich su giao dich cua tung vi.
- Validate chain.
- Tamper block #1.
- Validate lai de thay chain khong hop le.
- Reset blockchain de demo lai tu dau.

## Bang use case chuc nang moi

| Use case | Tac nhan | Mo ta | Ket qua |
| --- | --- | --- | --- |
| Tao vi | Nguoi dung | Nhap ten vi va nhan Create Wallet | He thong sinh address va cap token demo |
| Dang nhap vi | Nguoi dung | Nhap address de chon vi dang dung | Sender duoc dien tu dong khi gui giao dich |
| Gui giao dich | Nguoi dung | Nhap receiver va amount | Giao dich vao pending pool neu du so du |
| Mine block | Miner | Nhap dia chi miner va dao block | Block moi duoc tao, miner nhan reward va gas fee |
| Xem explorer | Nguoi dung | Mo Blockchain Explorer | Thay block, hash, nonce va danh sach transaction |
| Tim address | Nguoi dung | Nhap dia chi vi | Thay so du va lich su giao dich |
| Validate chain | Nguoi dung | Nhan Validate Blockchain | He thong bao chain hop le hoac chi ra block loi |
| Tamper block | Nguoi dung | Sua du lieu block da mine | Validate phat hien chain khong hop le |
| Doi difficulty | Nguoi dung | Nhap difficulty moi | Block moi se mat thoi gian mine tuong ung |
| Reset blockchain | Nguoi dung | Xac nhan reset | Tao lai genesis block va xoa du lieu demo |

## Han che

- Vi chi la mo phong, chua co private key, public key va chu ky so.
- He thong chay mot node, chua co mang ngang hang P2P.
- Smart Contract chi mo phong token account-based don gian.
- Gas fee co dinh, chua tinh theo do phuc tap cua giao dich.
- Du lieu JSON phu hop demo, chua phai database san xuat.
- Chua co co che dong bo chain giua nhieu node.

## Huong phat trien

- Bo sung chu ky so RSA/ECDSA cho giao dich.
- Tao nhieu node Flask va co che consensus.
- Them mempool nang cao va uu tien giao dich theo gas fee.
- Luu du lieu bang SQLite hoac PostgreSQL.
- Bo sung endpoint export bao cao block/transaction.
- Them phan quyen admin cho chuc nang tamper va reset.

## Noi dung thuyet trinh ngan

**Vi sao can tao vi?**
Vi la dinh danh cua nguoi dung tren blockchain. Moi vi co address rieng de gui, nhan va kiem tra so du token.

**Vi sao giao dich can dua vao pending pool?**
Pending pool la noi tap ket giao dich truoc khi duoc miner dua vao block. Dieu nay mo phong cach blockchain khong ghi giao dich ngay lap tuc ma can cho xac nhan.

**Mining block hoat dong the nao?**
Miner lay cac giao dich dang cho, tao block moi, sau do thay doi `nonce` lien tuc den khi hash cua block bat dau bang so luong so 0 theo difficulty.

**Proof of Work giup bao mat ra sao?**
Proof of Work bat miner ton cong tinh toan de tao block hop le. Neu ai sua du lieu block, hash thay doi va phai tinh lai Proof of Work cho block do va cac block sau.

**Tai sao blockchain co tinh bat bien?**
Moi block luu hash cua block truoc. Khi mot block bi sua, hash cua no thay doi, lam `previous_hash` cua block sau khong con khop. Vi vay viec sua du lieu se bi phat hien.

**Vi sao can validate chain?**
Validate chain giup kiem tra du lieu blockchain co bi sua hay loi khong. He thong tinh lai hash, kiem tra lien ket block va kiem tra Proof of Work.

**Gas fee va mining reward co y nghia gi?**
Gas fee la phi nguoi gui tra de giao dich duoc xu ly. Mining reward la phan thuong khuyen khich miner tham gia dao block va bao ve he thong.
