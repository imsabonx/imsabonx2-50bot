# SabonX2 50 Bot — Starter Project

এটি একটি অনলাইন-হোস্ট করার উপযোগী Flask প্রজেক্ট। বর্তমান সংস্করণ অনুমোদিত HTTPS URL-এর reachability/status পরীক্ষা করে। এটি Login করে ফর্ম Submit বা অন্য কোনো সাইটের task complete করে না; সেই কাজের জন্য নির্দিষ্ট সাইটের অনুমোদিত API/workflow লাগবে।

## লোকাল কম্পিউটারে চালানো

1. Python 3.11 বা তার নতুন সংস্করণ ইনস্টল করুন।
2. টার্মিনালে প্রজেক্ট ফোল্ডারে যান।
3. `pip install -r requirements.txt`
4. অনুমোদিত domain সেট করুন:
   - Linux/macOS: `export ALLOWED_DOMAINS=example.com,www.example.com`
   - Windows PowerShell: `$env:ALLOWED_DOMAINS="example.com,www.example.com"`
5. `python app.py`
6. ব্রাউজারে `http://127.0.0.1:8000` খুলুন।

`example.com`-এর বদলে নিজের বা পরীক্ষার অনুমতি থাকা domain বসান। Domain allowlist ফাঁকা থাকলে সব URL reject হবে।

## Render-এ অনলাইন হোস্ট করা

1. ZIP extract করে GitHub repository-তে ফাইলগুলো push করুন।
2. Render-এ **New + → Blueprint** বেছে repository connect করুন।
3. `render.yaml` ব্যবহার করে service তৈরি করুন।
4. Render-এর Environment settings-এ `ALLOWED_DOMAINS` সেট করুন, যেমন `yourdomain.com,www.yourdomain.com`।
5. Deploy শেষ হলে Render-এর দেওয়া URL খুলুন।

Hosting provider-এর বর্তমান নির্দেশনা ও পরিকল্পনার সীমা যাচাই করুন; free hosting-এ sleep/usage limits থাকতে পারে।

## কীভাবে ব্যবহার করবেন

- প্রতিটি লাইনে একটি HTTPS URL দিন।
- **Check links** চাপুন।
- রিপোর্টে Reachable, Failed বা Rejected status দেখুন।
- **Export CSV** দিয়ে রিপোর্ট ডাউনলোড করুন।

## সীমাবদ্ধতা ও নিরাপত্তা

- সর্বোচ্চ ৫০টি concurrent URL check; এটি ৫০টি autonomous browser agent নয়।
- HTTP response পাওয়া মানে কোনো business task সম্পন্ন হয়েছে এমন নয়।
- Redirect অনুসরণ করা হয় না।
- শুধুমাত্র allowlist করা domain গ্রহণ করা হয়; hostname-এর DNS public IP-তে resolve হতে হবে।
- নিজের বা স্পষ্ট অনুমতি থাকা সাইটেই ব্যবহার করুন।
- বাস্তব task completion verification-এর জন্য সাইটের official API বা server-side confirmation ব্যবহার করুন।
- Public deployment-এর আগে authentication, rate limiting, audit logs, CSRF/security review এবং monitoring যোগ করুন।
