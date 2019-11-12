# Job
バイトで作ったコードを少しいじって置きます。  

## 概要
講義中にマイクで「テスト」や「試験」という単語を検知し、テストに出そうな範囲をメモ・録音しておくプログラムです。

- rec_google(Google Speech to Text 使用)  
Google CloudのSpeech to Textを使ったプログラムです。精度が高いですが、オンライン環境が必要です。  
Raspberry Pi/Mac対応で、Macの場合はオプション"-m"をつけて実行する必要があります。  

- rec_julius(Julius使用)  
フリー音声認識ライブラリの[Julius](https://julius.osdn.jp/)を使ったプログラムです。  
ライブラリ自体をインストールしたあとはオフラインでも利用することができますが、Google Speechに比べて認識精度は低いです。