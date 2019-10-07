# UnitypackageValidator
Validate unitypackage for Virtual Exhibition

# 引数

## 共通

|Arg|Argument|値|説明|デフォルト|
|:--|:--|:--|:--|
| -b | --batch | - | バッチモードで起動します。このモードは以下の引数と一緒に使用します。 | - |
| -m | --mode | validator | unitypackageをチェックします。チェック内容は次章にて。 | (Default) |
| -m | --mode | makerule | 参照関連のルールを作成します。 | |
| -m | --mode | adjust | ファイルに対して調整を行います。 | |
| -i | --input | (unitypackages*) | 入力するunitypackageのパスを指定します。複数指定可能です。 | |
| -o | --output | (filepath) | 出力するjsonファイルのパスを指定します。指定しない場合はunitypackageと同じ場所に、同名のjsonファイルが作成されます。 | |
| -n | --rootname | (strings) | ルート名を指定します。 | - |
| -l | --log | debug / info / warning / error / fatal | 標準エラー出力に出力するログのレベルを指定します。 | warning |
| -q | --quiet | - | 標準出力に何も出力しないようにします。 | - |

## validatorモード
|Arg|Argument|値|説明|デフォルト|
|:--|:--|:--|:--|
| -r | --rule | (filepath / url) | ルールが記載されたjsonファイルのパス、もしくはURLを指定します。 | - |
| -g | --ignore | reference | unitypackage内の参照エラーを無視します。 | - |
| -g | --ignore | blackreference | 参照におけるブラックリストエラーを無視します。 | - |
| -g | --ignore | dirroot | ディレクトリルート名の規定外エラーを無視します。 | - |
| -g | --ignore | shaderroot | シェーダールート名の規定外エラーを無視します。 | - |
| -g | --ignore | material | マテリアル数エラーを無視します。 | - |
| -g | --ignore | blackfile | ファイル名・ファイル拡張子によるブラックリストを無視します。 | - |
| -g | --ignore | filepathlength | ファイルパスの長さエラーを無視します。 | - |

## makeruleモード

|Arg|Argument|値|説明|デフォルト|
|:--|:--|:--|:--|
| -wr | --whitereference | (unitypackages* / GUID strings*) | 外部参照に対するホワイトリスト。unitypackageを指定した場合は、含まれるファイルすべてが登録されます。複数指定できます。 | - |
| -br | --blackfileguid | (unitypackages* / GUID strings*) | 同梱ファイルGUIDに対するブラックリスト。unitypackageを指定した場合は、含まれるファイルすべてが登録されます。複数指定できます。 | - |
| -be | --blackfileext | (extension strings*) | 同梱ファイル拡張子におけるブラックリスト。複数指定できます。 | - |
| -bn | --blackfilename | (filename strings*) | 同梱ファイル名におけるブラックリスト。拡張子付きでも可能です。複数指定できます。| - |
| -dr | --dirroot | - | ディレクトリルート名の指定ルールを有効にします。 | （無効）|
| -sr | --shaderroot | - | シェーダールート名の指定ルールを有効にします。 | （無効） |
| -mt | --material | (int) | マテリアル数の上限を指定します。指定した数字以内に収める必要があります。| - |
| -fl | --filepathlength | (int) | 「Assets」を含めたファイルパスの最大長を指定します。指定した文字数以内に収める必要があります。 | 120 |

## adjustモード

* ファイル名・シェーダー名などを、規定ルート名でルートを作り、階層を移動します。

|Arg|Argument|値|説明|デフォルト|
|:--|:--|:--|:--|
| -r | --rule | (filepath / url) | ルールが記載されたjsonファイルのパス、もしくはURLを指定します。 | - |
| -dr | --dirroot | - | ディレクトリルートに対して変更を行います。 | （無効） |
| -sr | --shaderroot | - | シェーダールートに対して変更を行います。 | （無効） |

# チェックできる内容

## reference
prefabやマテリアル、シーンファイルなどが依存している外部コンポーネントが、同じunitypackageに存在するかどうかをチェックします。同じunitypackageに参照先が存在する場合、内部参照と呼びます。

## whitereference
referenceで同じunitypackageにない場合、共通で用意しているコンポーネントにあるかもしれません。これを外部参照と呼んでいます。同じunitypackage内に存在しなくてもよいGUIDを指定することができます。

## blackfileguid
同梱してはいけないコンポーネントをGUIDをもとにチェックします。

## blackfileext
同梱してはいけないファイルを拡張子をもとにチェックします。「.」は含めずに指定します。

## blackfilename
同梱してはいけないファイル名をチェックします。指定した文字列がファイル名に含まれるかどうかチェックするため、拡張が付いていてもチェック可能です。

## dirroot
同梱されているアセットのディレクトルートがrootnameになっているかチェックします。

## shaderroot
同梱されているシェーダー階層のルートがrootnameになっているかチェックします。

## material
同梱されているマテリアル数が規定以内かチェックします。実際に参照されていないマテリアルであっても、unitypackageに含まれていればマテリアル数としてカウントされます。

## filelength
同梱されているアセットのファイルパスが、規定された文字数以内かどうかチェックします。ファイルパスは「Assets」以下のパスでチェックされ、「Assets」を含めた文字数となります。
