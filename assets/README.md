# Assets Directory

This directory contains assets for the MOKA NEWS project.

## Logo

The MOKA NEWS logo (`logo.png`) is displayed at the top of the README.

### Adding the Logo

**Quick Setup** (Recommended):
```bash
# From the repository root, run:
./download-logo.sh
```

**Manual Download**:
1. Download the logo from: https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca
2. Save it as `assets/logo.png`

**Using curl**:
```bash
curl -L -o assets/logo.png "https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca"
```

**Using wget**:
```bash
wget -O assets/logo.png "https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca"
```

### Committing the Logo

After downloading, commit the logo to the repository:
```bash
git add assets/logo.png
git commit -m "Add MOKA NEWS logo"
git push
```
