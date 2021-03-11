"""
Setup i18n package
"""

import i18n

i18n.set('file_format', 'json')
i18n.set('enable_memoization', True)
i18n.set('skip_locale_root_data', True)
i18n.set('fallback', 'it-IT')
i18n.set('filename_format', '{locale}.{format}')
i18n.load_path.append('./locales')
