package com.medimitra.app;

import android.Manifest;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.speech.tts.TextToSpeech;
import android.view.LayoutInflater;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.OnBackPressedCallback;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "MediMitraPrefs";
    private static final String KEY_SERVER_URL = "server_url";

    private WebView webView;
    private SwipeRefreshLayout swipeRefreshLayout;
    private ProgressBar progressBar;
    private View layoutError;
    private TextView tvCurrentUrl;

    private ValueCallback<Uri[]> mFilePathCallback;
    private Uri mCameraImageUri;
    private SharedPreferences prefs;
    private TextToSpeech mTextToSpeech;

    // 1. Camera Runtime Permission Request
    private final ActivityResultLauncher<String> cameraPermissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestPermission(), isGranted -> {
                if (isGranted) {
                    launchDirectCamera();
                } else {
                    Toast.makeText(this, "Camera permission was not granted. Please select an image from your files.", Toast.LENGTH_LONG).show();
                    launchGalleryPicker();
                }
            });

    // 2. Direct Camera Capture Activity Result
    private final ActivityResultLauncher<Intent> cameraLauncher =
            registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result -> {
                if (mFilePathCallback == null) return;
                Uri[] results = null;
                if (result.getResultCode() == RESULT_OK && mCameraImageUri != null) {
                    results = new Uri[]{mCameraImageUri};
                }
                mFilePathCallback.onReceiveValue(results);
                mFilePathCallback = null;
            });

    // 3. Gallery / File Picker Activity Result
    private final ActivityResultLauncher<Intent> galleryLauncher =
            registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result -> {
                if (mFilePathCallback == null) return;
                Uri[] results = null;
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    if (result.getData().getClipData() != null) {
                        int count = result.getData().getClipData().getItemCount();
                        results = new Uri[count];
                        for (int i = 0; i < count; i++) {
                            results[i] = result.getData().getClipData().getItemAt(i).getUri();
                        }
                    } else if (result.getData().getData() != null) {
                        results = new Uri[]{result.getData().getData()};
                    }
                }
                mFilePathCallback.onReceiveValue(results);
                mFilePathCallback = null;
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);

        initViews();
        setupWebView();
        setupSwipeRefresh();
        setupBackNavigation();
        initTextToSpeech();

        // Request initial permissions if not yet granted
        checkAppPermissions();

        // Load the server URL
        loadMediMitra();
    }

    // App Runtime Permissions Request (Camera & Voice Audio)
    private final ActivityResultLauncher<String[]> appPermissionsLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestMultiplePermissions(), permissions -> {
                // Handled
            });

    private void checkAppPermissions() {
        java.util.List<String> needed = new java.util.ArrayList<>();
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.CAMERA);
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.RECORD_AUDIO);
        }
        if (!needed.isEmpty()) {
            appPermissionsLauncher.launch(needed.toArray(new String[0]));
        }
    }

    private void initViews() {
        webView = findViewById(R.id.webView);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);
        progressBar = findViewById(R.id.progressBar);
        layoutError = findViewById(R.id.layoutError);
        tvCurrentUrl = findViewById(R.id.tvCurrentUrl);

        Button btnRetry = findViewById(R.id.btnRetry);
        Button btnChangeServer = findViewById(R.id.btnChangeServer);

        btnRetry.setOnClickListener(v -> {
            showError(false);
            loadMediMitra();
        });

        btnChangeServer.setOnClickListener(v -> showServerUrlDialog());
    }

    private void setupWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setMediaPlaybackRequiresUserGesture(false);

        // App identification
        String defaultUA = settings.getUserAgentString();
        settings.setUserAgentString(defaultUA + " MediMitraApp/1.0");

        // Enable cookies for Flask session authentication
        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        cookieManager.setAcceptThirdPartyCookies(webView, true);

        // Native Text-to-Speech Javascript Bridge
        webView.addJavascriptInterface(new AndroidTtsBridge(), "AndroidTTS");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                if (url.startsWith("tel:") || url.startsWith("mailto:") || url.startsWith("whatsapp:")) {
                    try {
                        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                        startActivity(intent);
                        return true;
                    } catch (Exception e) {
                        return false;
                    }
                }
                return false;
            }

            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                progressBar.setVisibility(View.VISIBLE);
                showError(false);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                progressBar.setVisibility(View.GONE);
                swipeRefreshLayout.setRefreshing(false);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    showError(true);
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (newProgress < 100) {
                    progressBar.setVisibility(View.VISIBLE);
                    progressBar.setProgress(newProgress);
                } else {
                    progressBar.setVisibility(View.GONE);
                }
            }

            // Support WebRTC live camera streams if HTML requests camera directly
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(() -> request.grant(request.getResources()));
            }

            // Android input type="file" handler
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback,
                                             FileChooserParams fileChooserParams) {
                cleanupCallback();
                mFilePathCallback = filePathCallback;

                boolean isCapture = (fileChooserParams != null && fileChooserParams.isCaptureEnabled());
                showCameraChooserDialog(isCapture);
                return true;
            }
        });
    }

    private void showCameraChooserDialog(boolean preferCamera) {
        if (preferCamera) {
            // Direct camera requested via HTML capture="environment"
            requestAndLaunchCamera();
            return;
        }

        // Show native option dialog
        CharSequence[] options = {"📸 Take Photo with Camera", "🖼️ Choose from Gallery / Files"};
        new AlertDialog.Builder(this)
                .setTitle("Select Prescription or Medicine Photo")
                .setItems(options, (dialog, which) -> {
                    if (which == 0) {
                        requestAndLaunchCamera();
                    } else {
                        launchGalleryPicker();
                    }
                })
                .setOnCancelListener(dialog -> cleanupCallback())
                .show();
    }

    private void requestAndLaunchCamera() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
            launchDirectCamera();
        } else {
            cameraPermissionLauncher.launch(Manifest.permission.CAMERA);
        }
    }

    private void launchDirectCamera() {
        try {
            Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            File photoFile = createImageFile();
            if (photoFile != null) {
                mCameraImageUri = FileProvider.getUriForFile(
                        this,
                        getApplicationContext().getPackageName() + ".fileprovider",
                        photoFile
                );
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, mCameraImageUri);
                takePictureIntent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);

                // Grant URI write permission to camera apps
                List<ResolveInfo> resInfoList = getPackageManager().queryIntentActivities(takePictureIntent, PackageManager.MATCH_DEFAULT_ONLY);
                for (ResolveInfo resolveInfo : resInfoList) {
                    String packageName = resolveInfo.activityInfo.packageName;
                    grantUriPermission(packageName, mCameraImageUri, Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
                }

                cameraLauncher.launch(takePictureIntent);
            } else {
                Toast.makeText(this, "Could not prepare photo storage. Opening gallery...", Toast.LENGTH_SHORT).show();
                launchGalleryPicker();
            }
        } catch (Exception e) {
            Toast.makeText(this, "Camera error: " + e.getMessage() + ". Opening gallery...", Toast.LENGTH_SHORT).show();
            launchGalleryPicker();
        }
    }

    private void launchGalleryPicker() {
        try {
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType("image/*");
            intent.putExtra(Intent.EXTRA_MIME_TYPES, new String[]{"image/jpeg", "image/png", "image/webp", "image/bmp"});
            galleryLauncher.launch(Intent.createChooser(intent, "Select Prescription Photo"));
        } catch (Exception e) {
            Toast.makeText(this, "Could not open file manager: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            cleanupCallback();
        }
    }

    private void cleanupCallback() {
        if (mFilePathCallback != null) {
            mFilePathCallback.onReceiveValue(null);
            mFilePathCallback = null;
        }
    }

    private void setupSwipeRefresh() {
        swipeRefreshLayout.setColorSchemeResources(R.color.primary);
        swipeRefreshLayout.setOnRefreshListener(() -> webView.reload());

        // Prevent pull-to-refresh while scrolling down inside the web page
        webView.getViewTreeObserver().addOnScrollChangedListener(() -> {
            swipeRefreshLayout.setEnabled(webView.getScrollY() == 0);
        });
    }

    private void setupBackNavigation() {
        getOnBackPressedDispatcher().addCallback(this, new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                if (webView.canGoBack()) {
                    webView.goBack();
                } else {
                    setEnabled(false);
                    getOnBackPressedDispatcher().onBackPressed();
                }
            }
        });
    }

    private File createImageFile() throws IOException {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        String imageFileName = "MEDIMITRA_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        if (storageDir != null && !storageDir.exists()) {
            storageDir.mkdirs();
        }
        return File.createTempFile(imageFileName, ".jpg", storageDir);
    }

    private String getServerUrl() {
        String defaultUrl = isRunningOnEmulator()
                ? getString(R.string.emulator_server_url)
                : getString(R.string.default_server_url);

        return prefs.getString(KEY_SERVER_URL, defaultUrl);
    }

    private void loadMediMitra() {
        String url = getServerUrl();
        tvCurrentUrl.setText("Attempting to connect: " + url);
        webView.loadUrl(url);
    }

    private void showError(boolean visible) {
        if (visible) {
            layoutError.setVisibility(View.VISIBLE);
            webView.setVisibility(View.GONE);
            tvCurrentUrl.setText("Target Server: " + getServerUrl());
        } else {
            layoutError.setVisibility(View.GONE);
            webView.setVisibility(View.VISIBLE);
        }
    }

    private void showServerUrlDialog() {
        LayoutInflater inflater = LayoutInflater.from(this);
        View dialogView = inflater.inflate(R.layout.dialog_server_url, null);
        EditText etUrl = dialogView.findViewById(R.id.etServerUrl);

        etUrl.setText(getServerUrl());
        etUrl.setSelection(etUrl.getText().length());

        new AlertDialog.Builder(this)
                .setTitle("MediMitra Server URL")
                .setView(dialogView)
                .setPositiveButton("Save & Connect", (dialog, which) -> {
                    String newUrl = etUrl.getText().toString().trim();
                    if (!newUrl.isEmpty()) {
                        if (!newUrl.startsWith("http://") && !newUrl.startsWith("https://")) {
                            newUrl = "http://" + newUrl;
                        }
                        prefs.edit().putString(KEY_SERVER_URL, newUrl).apply();
                        Toast.makeText(this, "Connecting to " + newUrl, Toast.LENGTH_SHORT).show();
                        showError(false);
                        loadMediMitra();
                    }
                })
                .setNegativeButton("Cancel", null)
                .setNeutralButton("Reset Default", (dialog, which) -> {
                    String defaultUrl = isRunningOnEmulator()
                            ? getString(R.string.emulator_server_url)
                            : getString(R.string.default_server_url);
                    prefs.edit().putString(KEY_SERVER_URL, defaultUrl).apply();
                    showError(false);
                    loadMediMitra();
                })
                .show();
    }

    private boolean isRunningOnEmulator() {
        return Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MODEL.contains("Android SDK built for x86")
                || Build.MANUFACTURER.contains("Genymotion")
                || (Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic"));
    }

    private void initTextToSpeech() {
        try {
            mTextToSpeech = new TextToSpeech(this, status -> {
                if (status == TextToSpeech.SUCCESS && mTextToSpeech != null) {
                    mTextToSpeech.setLanguage(new Locale("hi", "IN"));
                }
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public class AndroidTtsBridge {
        @JavascriptInterface
        public void speak(String text, String langCode, float rate) {
            if (mTextToSpeech == null || text == null || text.trim().isEmpty()) return;
            runOnUiThread(() -> {
                try {
                    String cleanLang = (langCode != null && !langCode.isEmpty()) ? langCode : "en";
                    Locale loc = new Locale(cleanLang, "IN");
                    mTextToSpeech.setLanguage(loc);
                    mTextToSpeech.setSpeechRate(rate > 0 ? rate : 1.0f);
                    mTextToSpeech.speak(text, TextToSpeech.QUEUE_FLUSH, null, "medimitra_tts");
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }

        @JavascriptInterface
        public void stop() {
            if (mTextToSpeech != null) {
                runOnUiThread(() -> {
                    try {
                        mTextToSpeech.stop();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                });
            }
        }
    }

    @Override
    protected void onDestroy() {
        if (mTextToSpeech != null) {
            try {
                mTextToSpeech.stop();
                mTextToSpeech.shutdown();
            } catch (Exception e) {}
        }
        super.onDestroy();
    }
}
