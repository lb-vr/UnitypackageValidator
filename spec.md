
# ルールのリスト

Whitelist / Blacklistはどちらか選択

「操作」を実行する際にはエラーメッセージを残す

| ルール | ルールpy | Whitelist | Blacklist | 操作 |
| -- | -- | :--: | :--: | -- |
| ルートフォルダ名 | root_directory_filter| ● | ● | 違反を削除 |
| ファイル名・拡張子 | filename_filter| ● | ● | 違反を削除 |
| 同梱アセット | included_assets_filter | | ● | 違反を削除 |
| 改変禁止な共通アセット | common_assets_filter | | | エラーを表示して停止 |


# 操作機能

出展者に対して割り当てられる文字列（uuidなど）をIDと呼称する。

| ルール名 | ルールpy| 説明 |
| -- | -- | -- |
| 参照されていないアセットの排除 | noneed_assets_remover | 参照されていないアセットをリストアップし、排除する。 |
| 共通アセットで未改変のものを排除 | common_assets_remover | 共通アセットに含まれていて未改変のものを排除する |
| ルートフォルダの生成・ネスト | root_nester | ID、もしくは任意の文字列のフォルダ名の下に、全ファイルをネストさせる。 |
| ファイル名の変更 | files_prefix_renamer| 全てのファイル名を、ID、もしくは任意の文字列をprefixとしたファイル名にリネームする |
| shader名のネスト | shader_name_nester| shader階層を、ID、もしくは任意の文字列でネストする |
| GUIDの変換 | guid_remapper | アセットのuuidを再生成。マッピングを生成してテキストログに保存する。次回以降、このテキストをもとに、同じuuidからは同じuuidを生成するようにする。 |