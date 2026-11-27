# TierTube · Descargas para usuarios

**a.0.6.7.beta para Android, Windows x64 y Linux x86-64**

TierTube reúne búsqueda, reproducción, descargas autorizadas y listas locales. Elegí la descarga para tu dispositivo.

| Plataforma | Página | Archivo |
| --- | --- | --- |
| Android 8.0 o posterior | [Descarga Android](https://lionelvidal300-tech.github.io/tiertube-actualizaciones-usuarios/) | [APK de usuario](TierTube-a.0.6.7.beta-usuario.apk) |
| Windows x64 | [Descarga Windows](https://lionelvidal300-tech.github.io/tiertube-actualizaciones-usuarios/windows/) | [EXE portátil](windows/TierTube-a.0.6.7.beta-usuario.exe) |
| Linux x86-64 | [Descarga Linux](https://lionelvidal300-tech.github.io/tiertube-actualizaciones-usuarios/linux/) | [Binario portátil](linux/TierTube-a.0.6.7.beta-usuario) |

En esta versión, **Instagram** abre el perfil de soporte y **Correo** prepara un mensaje a `vidalnelson2026@gmail.com`. Android también comprueba que el nombre de versión del APK coincida con el catálogo antes de instalarlo.

## Instalar y actualizar

- **Android.** Si ya tenés la edición de usuario, instalá el APK encima de la versión anterior para conservar los datos.
- **Windows.** Cerrá TierTube y abrí el EXE nuevo. Se conserva la biblioteca del mismo perfil. El EXE incluye Tkinter.
- **Linux.** Descargá el binario, dale permiso de ejecución con `chmod +x TierTube-a.0.6.7.beta-usuario` y abrilo. Requiere Python 3.9+ con Tkinter. El binario abre una ventana nativa.
- **Próximas versiones.** Buscalas desde **Ajustes → Actualizaciones**. TierTube comprueba el paquete o el manifiesto firmado, y pide confirmación antes de descargar.

En Inicio podés elegir el idioma manualmente. **Comentarios** se abre desde Inicio o Ajustes y envía directamente al formulario de soporte cuando está habilitado.

## Archivo de versiones

- Android · [a.0.6.6.beta](TierTube-a.0.6.6.beta-usuario.apk) · [a.0.6.5.beta](TierTube-a.0.6.5.beta-usuario.apk) · [a.0.6.4.beta](TierTube-a.0.6.4.beta-usuario.apk) · [a.0.6.3.beta](TierTube-a.0.6.3.beta-usuario.apk) · [a.0.6.2.beta](TierTube-a.0.6.2.beta-usuario.apk)
- Windows · [a.0.6.6.beta](windows/TierTube-a.0.6.6.beta-usuario.exe) · [a.0.6.5.beta](windows/TierTube-a.0.6.5.beta-usuario.exe) · [a.0.6.4.beta](windows/TierTube-a.0.6.4.beta-usuario.exe)

[Manifiesto Android](user-android.json) · [Manifiesto Windows](windows.json) · [Manifiesto Linux](linux.json) · [SHA-256](SHA256SUMS)

- Linux · [a.0.6.6.beta](linux/TierTube-a.0.6.6.beta-usuario) · [a.0.6.5.beta](linux/TierTube-a.0.6.5.beta-usuario)

Desarrollado por Creative Revveal.

## Verificación de las actualizaciones de Android

[GitHub Actions](../../actions/workflows/android-release-check.yml) verifica el APK del catálogo público cuando cambia el canal de Android en `main`. Comprueba el paquete, el código de versión, el certificado y el SHA-256 publicado. Se puede ejecutar manualmente desde Actions.

Para activar VirusTotal, el titular debe crear el secreto de Actions `VT_API_KEY` en este repositorio. Actions consulta el informe por SHA-256. Si todavía no existe y la ejecución corresponde a un cambio en `main`, envía el APK de usuarios que ya se publicó. La ejecución manual consulta el informe disponible. Los APK de propietario permanecen en su canal privado.

El informe y el borrador de apelación están en el artefacto `comprobacion-android` de la ejecución. Si Play Protect bloquea el APK en un teléfono, completá el modelo, la versión de Android y el aviso exacto en el borrador antes de usar el formulario oficial. El estado de VirusTotal y el análisis de Play Protect se consultan por separado. La verificación en `main` corre sobre archivos que GitHub ya sirve. Para una prueba previa a anunciar una actualización, ejecutá el flujo manual en la rama que contiene el APK y el catálogo del candidato y probá ese mismo archivo en un teléfono.
