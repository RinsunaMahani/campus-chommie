"""
Receipt MECHANICS -- never receipt CONTENT.

THE SPLIT, AND WHY IT MATTERS:
    This package knows how to make a receipt SECURE and VERIFIABLE:
    reference numbers, QR payloads, signatures, verification hashes.

    It must NEVER know what a receipt SAYS: not the title, not who it is
    for, not what was paid for.

    A domain that ever issues a receipt owns its CONTENT (title, wording,
    footer) and calls the SAME mechanics here.

    Exactly the same shape as email templates: one sending engine, many
    domain-owned templates.

CURRENT STATUS -- deliberately minimal:
    reference.py is real; nothing in Campus Chommie issues receipts yet.

    qr.py, signing.py and verification.py are NOT implemented, on
    purpose. Real signing needs a server-held private key -- which the
    backend work now makes possible -- but building it before there is a
    real key, a real verification endpoint, and a real threat model
    would produce something that LOOKS verified without BEING verified,
    which is worse than no signature at all.
"""
